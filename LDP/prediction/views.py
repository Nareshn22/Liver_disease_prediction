import matplotlib
matplotlib.use('Agg')

import threading
import matplotlib.pyplot as plt
from django.http import JsonResponse, FileResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Prediction
import pickle
import logging
import traceback
from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_str
from reportlab.pdfgen import canvas
from io import BytesIO


logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'prediction/index.html', {'prediction': None, 'input_data': None})

# Function to plot feature importance
def plot_feature_importance(feature_names, feature_importances, feature_importance_path):
    plt.figure(figsize=(10, 6))
    plt.barh(feature_names, feature_importances)
    plt.xlabel('Feature Importance')
    plt.ylabel('Feature')
    plt.title('Feature Importance Plot')
    plt.gca().invert_yaxis()
    plt.tight_layout()

    # Save the plot to a file
    plt.savefig(feature_importance_path)
    plt.close()  # Close to free memory

@csrf_exempt
def predict(request):
    try:
        if request.method == 'POST':
            # Log the received data
            logger.info("Received POST request with data: %s", request.POST)
            
            # Extract features from the request
            features = [
                float(request.POST.get(f'feature{i}', 0)) for i in range(1, 11)
            ]

            # Load the machine learning model (consider caching this to avoid reloading on every request)
            with open('ensemble.pkl', 'rb') as file:
                model = pickle.load(file)

            # Make prediction
            prediction = model.predict([features])

            # Save prediction to the database
            prediction_obj = Prediction.objects.create(
                age=features[0],
                direct_bilirubin=features[1],
                alkaline_phosphotase=features[2],
                alamine_aminotransferase=features[3],
                aspartate_aminotransferase=features[4],
                total_proteins=features[5],
                albumin=features[6],
                albumin_and_globulin_ratio=features[7],
                gender_female=features[8],
                gender_male=features[9],
                prediction=prediction[0]
            )

            # Safely log the prediction action
            if request.user.is_authenticated:
                user_id = request.user.id
            else:
                user_id = None

            user = request.user if request.user.is_authenticated else None

    # Only log if there is an authenticated user
            if user:
                LogEntry.objects.log_action(
                user_id=user.id,
                content_type_id=None,  # Add actual content type ID if needed
                object_id=None,  # Use object ID if necessary
                object_repr="Liver Disease Prediction",  # Custom log description
                action_flag=1,  # Example action flag (e.g., for additions)
                change_message="Prediction result generated"
            
            )
            # Extract feature importances for the plot
            feature_names = ['Age', 'Direct Bilirubin', 'Alkaline Phosphotase', 'Alamine Aminotransferase', 
                             'Aspartate Aminotransferase', 'Total Proteins', 'Albumin', 
                             'Albumin and Globulin Ratio', 'Gender (Female)', 'Gender (Male)']
            feature_importances = model.feature_importances_

            # Create the feature importance plot in a separate thread to avoid blocking
            feature_importance_path = 'static/images/feature_importance.png'
            thread = threading.Thread(target=plot_feature_importance, args=(feature_names, feature_importances, feature_importance_path))
            thread.start()

            # Prepare the response data
            input_data = dict(zip(
                ['Age', 'Direct_Bilirubin', 'Alkaline_Phosphotase', 'Alamine_Aminotransferase', 
                 'Aspartate_Aminotransferase', 'Total_Proteins', 'Albumin', 
                 'Albumin_and_Globulin_Ratio', 'Gender_Female', 'Gender_male'], features
            ))

            response_data = {
                'prediction': prediction[0],
                'input_data': input_data,
                'feature_importance_graph': feature_importance_path,
                'prediction_id': prediction_obj.id
            }
            return JsonResponse(response_data)

    except Exception as e:
        logger.error("An error occurred: %s", e)
        logger.error(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def download_report(request, prediction_id):
    # Retrieve the Prediction object using the ID
    pred = Prediction.objects.get(id=prediction_id)

    # Create a file-like buffer to receive PDF data
    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    # Customize the PDF content
    p.setFont("Helvetica", 14)
    p.drawString(100, 800, "Liver Disease Prediction Report")
    
    # Add the prediction data to the PDF, using the fields from the Prediction model
    p.setFont("Helvetica", 12)
    p.drawString(100, 770, f"Age: {pred.age}")
    p.drawString(100, 750, f"Direct Bilirubin: {pred.direct_bilirubin}")
    p.drawString(100, 730, f"Alkaline Phosphatase: {pred.alkaline_phosphotase}")
    p.drawString(100, 710, f"Alamine Aminotransferase: {pred.alamine_aminotransferase}")
    p.drawString(100, 690, f"Aspartate Aminotransferase: {pred.aspartate_aminotransferase}")
    p.drawString(100, 670, f"Total Proteins: {pred.total_proteins}")
    p.drawString(100, 650, f"Albumin: {pred.albumin}")
    p.drawString(100, 630, f"Albumin and Globulin Ratio: {pred.albumin_and_globulin_ratio}")
    p.drawString(100, 610, f"Gender: {'Female' if pred.gender_female else 'Male'}")
    p.drawString(100, 590, f"Prediction: {pred.prediction}")
    p.drawString(100, 570, f"Date: {pred.timestamp.strftime('%Y-%m-%d')}")

    # Finalize PDF
    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='prediction_report.pdf')

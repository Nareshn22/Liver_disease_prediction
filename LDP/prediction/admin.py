from django.contrib import admin
from django.urls import path
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from django.urls import reverse
from .models import Prediction


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'age', 'direct_bilirubin', 'alkaline_phosphotase', 'alamine_aminotransferase',
        'aspartate_aminotransferase', 'total_proteins', 'albumin', 'albumin_and_globulin_ratio',
        'gender_female', 'gender_male', 'prediction', 'timestamp', 'download_link'
    )
    search_fields = ('id', 'prediction')
    list_filter = ('prediction',)
    ordering = ('-timestamp',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('download-report/<int:prediction_id>/', self.admin_site.admin_view(self.download_report), name='download_prediction_report'),
        ]
        return custom_urls + urls

    def download_link(self, obj):
        return format_html(
            '<a class="button" href="{}">Download PDF</a>',
            reverse('admin:download_prediction_report', args=[obj.id])
        )
    download_link.short_description = 'Download Report'
    download_link.allow_tags = True

    def download_report(self, request, prediction_id):
        from django.http import FileResponse
        from io import BytesIO
        from reportlab.pdfgen import canvas
        pred = Prediction.objects.get(id=prediction_id)
        
        buffer = BytesIO()
        p = canvas.Canvas(buffer)

        p.setFont("Helvetica", 14)
        p.drawString(100, 800, "Liver Disease Prediction Report")

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

        p.showPage()
        p.save()

        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='prediction_report.pdf')

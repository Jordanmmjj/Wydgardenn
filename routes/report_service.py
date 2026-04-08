from fpdf import FPDF
from datetime import datetime
import os

class ReportePDF(FPDF):
    def header(self):
        # Logo (Intentamos cargar el logo, si no hay ponemos texto)
        logo_path = os.path.join(os.getcwd(), 'static', 'img', 'logo.ico') # O un png si tienes
        if os.path.exists(logo_path):
            try:
                # Los ICO pueden fallar en FPDF, mejor si fuera un PNG
                # self.image(logo_path, 10, 8, 33) 
                pass
            except:
                pass
        
        self.set_font('helvetica', 'B', 20)
        self.set_text_color(40, 114, 51) # Color verde WyGarden
        self.cell(0, 10, 'WYDGARDEN - REPORTE DE VENTAS', border=0, ln=1, align='C')
        self.ln(10)
        self.set_font('helvetica', 'I', 10)
        self.set_text_color(100)
        self.cell(0, 10, f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 0, 0, 'C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

def generar_pdf_ventas(ventas, titulo_periodo="GENERAL"):
    pdf = ReportePDF()
    pdf.add_page()
    
    # Título de tabla
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(0, 10, f"Resumen de Ventas: {titulo_periodo}", 0, 1, 'L')
    pdf.ln(5)
    
    # Encabezados de Tabla
    pdf.set_fill_color(40, 114, 51) # Fondo verde para cabecera
    pdf.set_text_color(255, 255, 255) # Texto blanco
    pdf.set_font('helvetica', 'B', 10)
    
    col_widths = [45, 60, 45, 40]
    headers = ['Fecha', 'Cliente', 'ID Pedido', 'Total ($)']
    
    for i, h in enumerate(headers):
        pdf.cell(col_widths[i], 10, h, 1, 0, 'C', fill=True)
    pdf.ln()
    
    # Filas de Datos
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('helvetica', '', 9)
    total_acumulado = 0
    
    for v in ventas:
        # Formatear fecha
        try:
            f_str = v.fecha_venta.strftime('%d/%m/%Y %H:%M') if v.fecha_venta else "S/F"
        except:
            f_str = "S/F"
            
        cliente_nombre = f"{v.usuario.nombres} {v.usuario.apellidos}" if v.usuario else "Desconocido"
        
        pdf.cell(col_widths[0], 10, f_str, 1)
        pdf.cell(col_widths[1], 10, cliente_nombre[:25], 1) # Recortamos si es muy largo
        pdf.cell(col_widths[2], 10, str(v.id_pedido), 1, 0, 'C')
        pdf.cell(col_widths[3], 10, f"${v.total:,.0f}", 1, 0, 'R')
        pdf.ln()
        total_acumulado += v.total
    
    # Fila de gran total
    pdf.ln(5)
    pdf.set_font('helvetica', 'B', 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(sum(col_widths[:-1]), 12, "TOTAL RECAUDADO EN EL PERÍODO:", 1, 0, 'R', fill=True)
    pdf.cell(col_widths[-1], 12, f"${total_acumulado:,.0f}", 1, 1, 'R', fill=True)
    
    # Manejar salida para fpdf o fpdf2
    try:
        # En fpdf2 output() sin parámetros devuelve bytes
        return pdf.output()
    except:
        # En fpdf clásico necesitamos dest='S'
        return pdf.output(dest='S')

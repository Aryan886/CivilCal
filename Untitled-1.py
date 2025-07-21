def generate_pdf(self):
    # Get filename and ensure pdfs directory exists
    filename = self.pdf_filename_edit.text().strip()
    if not filename.lower().endswith('.pdf'):
        filename += '.pdf'
    pdf_dir = os.path.join(os.getcwd(), 'pdfs')
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, filename)

    # Prepare CSV filename and directory
    csv_filename = filename.replace('.pdf', '.csv')
    csv_path = os.path.join(pdf_dir, csv_filename)

    # Prepare data for PDF table and CSV
    headers = ["Beam Type", "Beam No.", "Bend len 1", "Bend len 2", "Quantity", "Cutting-length (per bar)", "Weight"]
    data = [headers]
    grouped = defaultdict(list)
    for res in self.results:
        if 'd' in res:
            grouped[res["d"]].append(res)
        elif 'diameter' in res:
            grouped[res["diameter"].__str__()].append(res)
        else:
            grouped[res["type"]].append(res)
    
    for key in sorted(grouped.keys(), key=lambda x: str(x)):
        # Add a header row for each group
        data.append([f"Bar Diameter: {key} mm", '', '', '', '', '', ''])
        for res in grouped[key]:
            # For Cantilever
            if res.get("type") == "Cantilever":
                row = [
                    str(res.get("type", "")),
                    str(res.get("beam no.", "")),
                    "-", "-",
                    str(res.get("quantity", "")),
                    str(res.get("length per bar", "")),
                    str(res.get("weight", "")),
                ]
            # For stirrups
            elif res.get("spacing type") == "uniform":
                row = [
                    str(res.get("type", "")),
                    str(res.get("beam no.", "")),
                    "-", "-",
                    str(res.get("quantity", "")),
                    str(res.get("num_stirrups", "")),
                    str(res.get("total_weight", "")),
                ]
            # For Top Steel
            elif res.get("type") == "Top Steel":
                row = [
                    str(res.get("type", "")),
                    str(res.get("beam no.", "")),
                    str(res.get("bend length1", "")),
                    str(res.get("bend length2", "")),
                    str(res.get("quantity", "")),
                    str(res.get("length per bar", "")),
                    str(res.get("weight", "")),
                ]
            # For Bottom Steel
            elif res.get("type") == "Bottom Steel":
                row = [
                    str(res.get("type", "")),
                    str(res.get("beam no.", "")),
                    str(res.get("bend length1", "")),
                    str(res.get("bend length2", "")),
                    str(res.get("quantity", "")),
                    str(res.get("length per bar", "")),
                    str(res.get("weight", "")),
                ]
            # For Slab
            elif res.get("type") == "One-way":
                row = [
                    str(res.get("type", "")),
                    str(res.get("diameter", "")),
                    "-", "-",
                    str(res.get("quantity", "")),
                    str(res.get("main bars", "")),
                    str(res.get("total weight", "")),
                ]
            else:
                row = [str(res.get(h, "")) for h in headers]
            data.append(row)
    
    # Generate PDF
    try:
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        elements.append(Paragraph("Cutting Length Results", styles['Title']))
        elements.append(Spacer(1, 12))
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
        doc.build(elements)
        pdf_success = True
        pdf_error = None
    except Exception as e:
        pdf_success = False
        pdf_error = str(e)

    # Generate CSV
    try:
        import csv
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(data)
        csv_success = True
        csv_error = None
    except Exception as e:
        csv_success = False
        csv_error = str(e)

    # Show appropriate message based on results
    if pdf_success and csv_success:
        QMessageBox.information(self, "Success", f"PDF saved to {pdf_path}\nCSV saved to {csv_path}")
    elif pdf_success and not csv_success:
        QMessageBox.warning(self, "Partial Success", f"PDF saved to {pdf_path}\nCSV failed: {csv_error}")
    elif not pdf_success and csv_success:
        QMessageBox.warning(self, "Partial Success", f"CSV saved to {csv_path}\nPDF failed: {pdf_error}")
    else:
        QMessageBox.critical(self, "Error", f"Both exports failed:\nPDF: {pdf_error}\nCSV: {csv_error}")
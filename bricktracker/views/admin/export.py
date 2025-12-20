import csv
import io

from flask import (
    Blueprint,
    request,
)
from flask_login import login_required
from werkzeug.wrappers.response import Response

from ..exceptions import exception_handler
from ...part_list import BrickPartList
from ...set_list import BrickSetList

admin_export_page = Blueprint(
    'admin_export',
    __name__,
    url_prefix='/admin/export'
)


# Export all sets to Rebrickable CSV format
@admin_export_page.route('/sets/rebrickable-csv', methods=['GET'])
@login_required
@exception_handler(__file__)
def export_sets_rebrickable() -> Response:

    set_list = BrickSetList()
    all_sets = set_list.all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(['Set Number', 'Quantity', 'Includes Spares', 'Inventory Ver'])

    for set_item in all_sets.records:
        writer.writerow([
            set_item.fields.set,
            1,  # Each set instance counts as 1
            'True',  # BrickTracker tracks spares separately
            1  # Inventory version (always 1 for now)
        ])

    # Prepare response
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=bricktracker_sets_rebrickable.csv'}
    )


# Export all parts to Rebrickable CSV format
@admin_export_page.route('/parts/rebrickable-csv', methods=['GET'])
@login_required
@exception_handler(__file__)
def export_parts_rebrickable() -> Response:

    owner_id = request.args.get('owner')
    color_id = request.args.get('color')
    theme_id = request.args.get('theme')
    year = request.args.get('year')

    part_list = BrickPartList()
    part_list.all_filtered(owner_id, color_id, theme_id, year)

    part_quantities = {}
    for part in part_list.records:
        key = (part.fields.part, part.fields.color)
        if key in part_quantities:
            part_quantities[key] += part.fields.quantity
        else:
            part_quantities[key] = part.fields.quantity

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(['Part', 'Color', 'Quantity'])

    for (part_num, color_id), quantity in sorted(part_quantities.items()):
        writer.writerow([part_num, color_id, quantity])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=bricktracker_parts_rebrickable.csv'}
    )


# Export all parts to LEGO Pick-a-Brick CSV format
@admin_export_page.route('/parts/lego-csv', methods=['GET'])
@login_required
@exception_handler(__file__)
def export_parts_lego() -> Response:

    owner_id = request.args.get('owner')
    color_id = request.args.get('color')
    theme_id = request.args.get('theme')
    year = request.args.get('year')

    part_list = BrickPartList()
    part_list.all_filtered(owner_id, color_id, theme_id, year)

    element_quantities = {}
    for part in part_list.records:
        if part.fields.element:
            element_id = part.fields.element
            if element_id in element_quantities:
                element_quantities[element_id] += part.fields.quantity
            else:
                element_quantities[element_id] = part.fields.quantity

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(['elementId', 'quantity'])

    for element_id, quantity in sorted(element_quantities.items()):
        writer.writerow([element_id, quantity])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=bricktracker_parts_lego.csv'}
    )


# Export all parts to BrickLink XML format
@admin_export_page.route('/parts/bricklink-xml', methods=['GET'])
@login_required
@exception_handler(__file__)
def export_parts_bricklink() -> Response:

    owner_id = request.args.get('owner')
    color_id = request.args.get('color')
    theme_id = request.args.get('theme')
    year = request.args.get('year')

    part_list = BrickPartList()
    part_list.all_filtered(owner_id, color_id, theme_id, year)

    part_quantities = {}
    for part in part_list.records:
        part_num = part.fields.bricklink_part_num or part.fields.part
        color_id = part.fields.bricklink_color_id or part.fields.color

        key = (part_num, color_id)
        if key in part_quantities:
            part_quantities[key] += part.fields.quantity
        else:
            part_quantities[key] = part.fields.quantity

    xml_lines = ['<INVENTORY>']

    for (part_num, color_id), quantity in sorted(part_quantities.items()):
        xml_lines.append(
            f'<ITEM><ITEMTYPE>P</ITEMTYPE><ITEMID>{part_num}</ITEMID>'
            f'<COLOR>{color_id}</COLOR><MINQTY>{quantity}</MINQTY></ITEM>'
        )

    xml_lines.append('</INVENTORY>')
    xml_content = ''.join(xml_lines)

    return Response(
        xml_content,
        mimetype='application/xml',
        headers={'Content-Disposition': 'attachment;filename=bricktracker_parts_bricklink.xml'}
    )


# Export missing/damaged parts to Rebrickable CSV format
@admin_export_page.route('/problems/rebrickable-csv', methods=['GET'])
@login_required
@exception_handler(__file__)
def export_problems_rebrickable() -> Response:

    owner_id = request.args.get('owner')
    color_id = request.args.get('color')
    theme_id = request.args.get('theme')
    year = request.args.get('year')

    part_list = BrickPartList()
    part_list.problem_filtered(owner_id, color_id, theme_id, year)

    part_quantities = {}
    for part in part_list.records:
        qty = (part.fields.missing or 0) + (part.fields.damaged or 0)
        if qty > 0:
            key = (part.fields.part, part.fields.color)
            if key in part_quantities:
                part_quantities[key] += qty
            else:
                part_quantities[key] = qty

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(['Part', 'Color', 'Quantity'])

    for (part_num, color_id), quantity in sorted(part_quantities.items()):
        writer.writerow([part_num, color_id, quantity])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=bricktracker_problems_rebrickable.csv'}
    )


# Export missing/damaged parts to LEGO Pick-a-Brick CSV format
@admin_export_page.route('/problems/lego-csv', methods=['GET'])
@login_required
@exception_handler(__file__)
def export_problems_lego() -> Response:

    owner_id = request.args.get('owner')
    color_id = request.args.get('color')
    theme_id = request.args.get('theme')
    year = request.args.get('year')

    part_list = BrickPartList()
    part_list.problem_filtered(owner_id, color_id, theme_id, year)

    element_quantities = {}
    for part in part_list.records:
        qty = (part.fields.missing or 0) + (part.fields.damaged or 0)
        if qty > 0 and part.fields.element:
            element_id = part.fields.element
            if element_id in element_quantities:
                element_quantities[element_id] += qty
            else:
                element_quantities[element_id] = qty

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(['elementId', 'quantity'])

    for element_id, quantity in sorted(element_quantities.items()):
        writer.writerow([element_id, quantity])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=bricktracker_problems_lego.csv'}
    )


# Export missing/damaged parts to BrickLink XML format
@admin_export_page.route('/problems/bricklink-xml', methods=['GET'])
@login_required
@exception_handler(__file__)
def export_problems_bricklink() -> Response:

    owner_id = request.args.get('owner')
    color_id = request.args.get('color')
    theme_id = request.args.get('theme')
    year = request.args.get('year')

    part_list = BrickPartList()
    part_list.problem_filtered(owner_id, color_id, theme_id, year)

    part_quantities = {}
    for part in part_list.records:
        qty = (part.fields.missing or 0) + (part.fields.damaged or 0)
        if qty > 0:
            part_num = part.fields.bricklink_part_num or part.fields.part
            color_id = part.fields.bricklink_color_id or part.fields.color

            key = (part_num, color_id)
            if key in part_quantities:
                part_quantities[key] += qty
            else:
                part_quantities[key] = qty

    xml_lines = ['<INVENTORY>']

    for (part_num, color_id), quantity in sorted(part_quantities.items()):
        xml_lines.append(
            f'<ITEM><ITEMTYPE>P</ITEMTYPE><ITEMID>{part_num}</ITEMID>'
            f'<COLOR>{color_id}</COLOR><MINQTY>{quantity}</MINQTY></ITEM>'
        )

    xml_lines.append('</INVENTORY>')
    xml_content = ''.join(xml_lines)

    return Response(
        xml_content,
        mimetype='application/xml',
        headers={'Content-Disposition': 'attachment;filename=bricktracker_problems_bricklink.xml'}
    )

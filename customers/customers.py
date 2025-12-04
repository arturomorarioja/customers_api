from flask import Blueprint, request, jsonify, url_for
from customers.database import get_db, format_db_data
from urllib.parse import urlencode

bp = Blueprint('customers', __name__)


def add_customer_links(customer: dict) -> dict:
    """Add HATEOAS links to a single customer representation."""
    customer_id = customer['customer_id']
    customer['links'] = [
        {
            'rel': 'self',
            'method': 'GET',
            'href': url_for('customers.get_customer_by_id', customer_id=customer_id, _external=True)
        },
        {
            'rel': 'update',
            'method': 'PUT',
            'href': url_for('customers.update_customer', customer_id=customer_id, _external=True)
        },
        {
            'rel': 'delete',
            'method': 'DELETE',
            'href': url_for('customers.delete_customer', customer_id=customer_id, _external=True)
        },
        {
            'rel': 'collection',
            'method': 'GET',
            'href': url_for('customers.get_customers', _external=True)
        }
    ]
    return customer


def collection_links(search_param=None, offset=0, size=5, total_items=0):
    """Build top-level links for the customer collection, including pagination."""
    base_url = url_for('customers.get_customers', _external=True)

    def build_url(offset_value):
        query = {}
        if search_param:
            query['s'] = search_param
        query['offset'] = offset_value
        query['size'] = size
        return f'{base_url}?{urlencode(query)}'

    links = [
        {
            'rel': 'self',
            'method': 'GET',
            'href': build_url(offset)
        },
        {
            'rel': 'create',
            'method': 'POST',
            'href': url_for('customers.create_customers', _external=True)
        },
        {
            'rel': 'search',
            'method': 'GET',
            'href': f'{base_url}?s={{query}}&offset=0&size={size}'
        }
    ]

    # Previous page link
    if offset > 0:
        prev_offset = max(offset - size, 0)
        links.append({
            'rel': 'prev',
            'method': 'GET',
            'href': build_url(prev_offset)
        })

    # Next page link
    if offset + size < total_items:
        next_offset = offset + size
        links.append({
            'rel': 'next',
            'method': 'GET',
            'href': build_url(next_offset)
        })

    return links


def error_message(customer_id: str | int | None = None):
    if customer_id is None:
        message = {'error': 'Incorrect parameters'}
    else:
        message = {'error': f'Customer with ID {customer_id} not found'}
    message['links'] = [
        {
            'rel': 'collection',
            'method': 'GET',
            'href': url_for('customers.get_customers', _external=True)
        },
        {
            'rel': 'create',
            'method': 'POST',
            'href': url_for('customers.create_customers', _external=True)
        }
    ]
    return jsonify(message)


# Search customers + Get all customers
@bp.route('/customers', methods=['GET'])
def get_customers():
    db = get_db()

    # Query parameters
    search_param = request.args.get('s', default=None, type=str)
    offset = request.args.get('offset', default=0, type=int)
    size = request.args.get('size', default=5, type=int)

    # Basic validation
    if offset < 0 or size <= 0:
        return jsonify({
            'error': 'Invalid pagination parameters. Offset must be >= 0 and size must be > 0.'
        }), 400

    # Base fragments
    select_sql = '''
        SELECT 
            nCustomerID, cFirstName, cLastName, cPhoneNo, cAddress, dOnboarding 
        FROM customer
    '''
    count_sql = 'SELECT COUNT(*) FROM customer'
    where_sql = ''
    params = []

    # Optional search condition
    if search_param:
        where_sql = '''
            WHERE cFirstName LIKE ?
               OR cLastName LIKE ?
        '''
        params = [f'%{search_param}%', f'%{search_param}%']

    # Total count (for pagination metadata and next/prev)
    total_items = db.execute(count_sql + ' ' + where_sql, params).fetchone()[0]

    # Data query with ordering and pagination
    data_sql = select_sql + ' ' + where_sql + '''
        ORDER BY dOnboarding DESC
        LIMIT ? OFFSET ?
    '''
    data_params = params + [size, offset]

    rows = db.execute(data_sql, data_params).fetchall()
    customers = [format_db_data(row) for row in rows]
    customers = [add_customer_links(c) for c in customers]

    response_body = {
        'items': customers,
        'pagination': {
            'offset': offset,
            'size': size,
            'total_items': total_items
        },
        'links': collection_links(
            search_param=search_param,
            offset=offset,
            size=size,
            total_items=total_items
        )
    }
    return jsonify(response_body), 200


# Create new customer
@bp.route('/customers', methods=['POST'])
def create_customers():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    phone_no = request.form.get('phone_no')
    address = request.form.get('address')
    onboarding_date = request.form.get('onboarding_date')

    if first_name and last_name and address and onboarding_date:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            '''
            INSERT INTO customer
                (cFirstName, cLastName, cPhoneNo, cAddress, dOnboarding)
            VALUES
                (?, ?, ?, ?, ?)
            ''',
            (first_name, last_name, phone_no, address, onboarding_date)
        )
        customer_id = cursor.lastrowid
        cursor.close()
        db.commit()

        # Fetch the newly created customer to return a full representation
        row = db.execute(
            '''
            SELECT
                nCustomerID, cFirstName, cLastName, cPhoneNo, cAddress, dOnboarding
            FROM customer
            WHERE nCustomerID = ?
            ''',
            (customer_id,)
        ).fetchone()

        customer = format_db_data(row)
        customer = add_customer_links(customer)

        return jsonify({
            'message': 'Customer successfully created',
            'customer': customer
        }), 201
    else:
        return error_message(None), 400


# Get customer by ID
@bp.route('/customers/<int:customer_id>', methods=['GET'])
def get_customer_by_id(customer_id: int):
    db = get_db()
    customer = db.execute(
        '''
        SELECT
            nCustomerID, cFirstName, cLastName, cPhoneNo, cAddress, dOnboarding
        FROM customer
        WHERE nCustomerID = ?
        ''',
        (str(customer_id),)
    ).fetchone()
    if customer:
        customer_dict = format_db_data(customer)
        customer_dict = add_customer_links(customer_dict)
        return jsonify(customer_dict), 200
    else:
        return error_message(customer_id), 404


# Update customer data
@bp.route('/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id: int):
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    phone_no = request.form.get('phone_no')
    address = request.form.get('address')
    onboarding_date = request.form.get('onboarding_date')

    if first_name or last_name or phone_no or address or onboarding_date:
        db = get_db()

        # Check that the customer exists
        existing = db.execute(
            'SELECT nCustomerID FROM customer WHERE nCustomerID = ?',
            (customer_id,)
        ).fetchone()
        if not existing:
            return error_message(customer_id), 404

        params = []
        sql = 'UPDATE customer SET '
        first_field_added = False

        if first_name:
            sql = sql + 'cFirstName = ?'
            params.append(first_name)
            first_field_added = True
        if last_name:
            sql = sql + (', cLastName = ?' if first_field_added else 'cLastName = ?')
            params.append(last_name)
            first_field_added = True
        if phone_no:
            sql = sql + (', cPhoneNo = ?' if first_field_added else 'cPhoneNo = ?')
            params.append(phone_no)
            first_field_added = True
        if address:
            sql = sql + (', cAddress = ?' if first_field_added else 'cAddress = ?')
            params.append(address)
            first_field_added = True
        if onboarding_date:
            sql = sql + (', dOnboarding = ?' if first_field_added else 'dOnboarding = ?')
            params.append(onboarding_date)

        sql = sql + ' WHERE nCustomerID = ?'
        params.append(customer_id)

        db.execute(sql, tuple(params))
        db.commit()

        # Return the updated representation
        row = db.execute(
            '''
            SELECT
                nCustomerID, cFirstName, cLastName, cPhoneNo, cAddress, dOnboarding
            FROM customer
            WHERE nCustomerID = ?
            ''',
            (customer_id,)
        ).fetchone()

        customer = format_db_data(row)
        customer = add_customer_links(customer)

        return jsonify({
            'message': f'Customer ID {customer_id} successfully updated',
            'customer': customer
        }), 200
    else:
        return error_message(None), 400


# Delete customer
@bp.route('/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id: int):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        '''
        DELETE FROM customer
        WHERE nCustomerID = ?
        ''',
        (customer_id,)
    )
    deleted_rows = cursor.rowcount
    db.commit()
    cursor.close()
    if deleted_rows > 0:
        return jsonify({
            'message': f'Customer ID {customer_id} successfully deleted',
            'links': [
                {
                    'rel': 'collection',
                    'method': 'GET',
                    'href': url_for('customers.get_customers', _external=True)
                },
                {
                    'rel': 'create',
                    'method': 'POST',
                    'href': url_for('customers.create_customers', _external=True)
                }
            ]
        }), 200
    else:
        return error_message(customer_id), 404
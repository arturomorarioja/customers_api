from flask import Blueprint, request, jsonify
from customers.database import get_db, format_db_data

def error_message(customer_id=''):
    if customer_id == '':
        message = {'error': 'Incorrect parameters'}
    else:
        message = {'error': f'Customer with ID {customer_id} not found'}
    return jsonify(message)

bp = Blueprint('customers', __name__)

# Search customers + Get all customers
@bp.route('/customers', methods=['GET'])
def get_customers():
    db = get_db()
    sql = '''
        SELECT 
            nCustomerID, cFirstName, cLastName, cPhoneNo, cAddress, dOnboarding 
        FROM customer 
    '''
    search_param = request.args.get('s')
    print(search_param)
    if search_param:        # Search endpoint
        sql = sql + '''
            WHERE cFirstName LIKE ?
            OR cLastName LIKE ?
            ORDER BY dOnboarding DESC
        '''
        print(sql)
        customers = db.execute(
            sql, (f'%{search_param}%', f'%{search_param}%')
        ).fetchall()
    else:                   # Get all customers endpoint
        sql = sql + ' ORDER BY dOnboarding DESC'
        customers = db.execute(sql).fetchall()
    customers = [format_db_data(row) for row in customers]
    return jsonify(customers), 200

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
        return jsonify({'Customer ID': customer_id}), 201
    else:
        return error_message(), 400

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
        (str(customer_id),)     # The trailing comma indicates that this is an iterable
    ).fetchone()
    if customer:
        return jsonify(format_db_data(customer)), 200
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
        params = []
        sql = 'UPDATE customer SET '        
        if first_name: 
            sql = sql + 'cFirstName = ?'
            params.append(first_name)
        if last_name: 
            sql = sql + ', cLastName = ?'
            params.append(last_name)
        if phone_no: 
            sql = sql + ', cPhoneNo = ?'
            params.append(phone_no)
        if address: 
            sql = sql + ', cAddress = ?'
            params.append(address)
        if onboarding_date: 
            sql = sql + ', dOnboarding = ?'
            params.append(onboarding_date)
        sql = sql + ' WHERE nCustomerID = ?'
        params.append(customer_id)

        db.execute(sql, tuple(params))
        db.commit()
        return jsonify({'message': f'Customer ID {customer_id} successfully updated'}), 200
    else:
        return error_message(), 400

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
        return jsonify({'message': f'Customer ID {customer_id} successfully deleted'}), 200
    else:
        return error_message(customer_id), 404
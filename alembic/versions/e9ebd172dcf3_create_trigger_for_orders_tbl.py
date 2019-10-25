"""create trigger for orders tbl

Revision ID: e9ebd172dcf3
Revises: 3ad572cfaf15
Create Date: 2019-10-25 11:58:16.442569

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = 'e9ebd172dcf3'
down_revision = '3ad572cfaf15'
branch_labels = None
depends_on = None


def upgrade():
	connection = op.get_bind()
	trigger = text(
	"""
		CREATE OR REPLACE FUNCTION orders_event() RETURNS TRIGGER AS $$
		DECLARE
		record RECORD;
		payload JSON;
		BEGIN
		IF (TG_OP = 'DELETE') THEN
		record = OLD;
		ELSE
		record = NEW;
		END IF;
		payload = json_build_object('table', TG_TABLE_NAME,
		                        'action', TG_OP,
		                        'data', row_to_json(record));
		PERFORM pg_notify('orders', payload::text);
		RETURN NULL;
		END;
		$$ LANGUAGE plpgsql;
		CREATE TRIGGER notify_order_event
		AFTER INSERT OR UPDATE OR DELETE ON orders
		FOR EACH ROW EXECUTE PROCEDURE orders_event();
	""")
	connection.execute(trigger)



def downgrade():
    drop_trigger = text("""
		drop trigger notify_order_event on orders;
		""")
    connection = op.get_bind()
    connection.execute(drop_trigger)

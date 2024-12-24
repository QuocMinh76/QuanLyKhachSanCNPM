# task.py
from apscheduler.schedulers.background import BackgroundScheduler

# Create the scheduler instance
scheduler = BackgroundScheduler()


def check_booking_orders():
    from dao import get_expired_booking_orders, update_booking_order_status_and_rooms
    from appQLKS import app

    with app.app_context():
        app.logger.info("Checking expired booking orders...")
        try:
            expired_orders = get_expired_booking_orders()
            if expired_orders:
                for order in expired_orders:
                    update_booking_order_status_and_rooms(order)
                    app.logger.info(f"Booking Order {order.id} has been cancelled and rooms availability updated.")
            else:
                app.logger.info("No expired orders found.")

            app.logger.info("Periodic task running: Checked booking orders for expiration.")
        except Exception as e:
            app.logger.error(f"Error occurred while checking booking orders: {e}")


def schedule_periodic_task():
    from appQLKS import app
    check_interval = app.config['CHECK_INTERVAL_HOURS']

    # Schedule the task to run every 24 hours
    # scheduler.add_job(func=check_booking_orders, trigger="interval", hours=check_interval)
    scheduler.add_job(func=check_booking_orders, trigger="interval", minutes=1) #check
    scheduler.start()

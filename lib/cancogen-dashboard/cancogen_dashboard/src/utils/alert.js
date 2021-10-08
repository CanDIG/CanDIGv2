import React from 'react';
import NotificationAlert from 'react-notification-alert';

/*
 * Return an object for NotificationAlert
 * @param {message}... message to be displayed on notification
 * @param {type}... This is the color of the notification and can be one of,
 * according to reactstrap colors for alerts:
    - primary
    - secondary
    - success
    - danger
    - warning
    - info
    - light
    - dark
 */
export function createNotificationObject(message, type = 'info') {
  return {
    place: 'tc',
    message: (
      <div>
        <b>{message}</b>
      </div>
    ),
    type,
    icon: 'nc-icon nc-bell-55',
    autoDismiss: 7,
  };
}

/* Displays the notification message
 * @param {refObject}... Object created at the React component using useRef(null)
 * @param {message}... message to be displayed on notification
 * @param {type}... This is the color of the notification and can be one of,
 * according to reactstrap colors for alerts:
    - primary
    - secondary
    - success
    - danger
    - warning
    - info
    - light
    - dark
 */
export function notify(refObject, message, type = 'info') {
  refObject.current.notificationAlert(createNotificationObject(message, type));
}

export { NotificationAlert };

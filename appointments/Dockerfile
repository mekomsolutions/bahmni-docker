# Not doing much in this file since we're using the official Bahmni Appointments image.
# However, we must keep maintaining our own image to make sure ARM images are built.


FROM bahmni/appointments
RUN apk add curl iproute2 iputils less nano ca-certificates tzdata
ARG TIMEZONE
RUN ln -s /usr/share/zoneinfo/$TIMEZONE /etc/localtime

There’s nothing about the device that indicates what user has the device assigned, but when data is recorded, it must be tagged with the user from whom it was recorded. Rather than put on device manufacturers to understand how to keep track of user IDs, the device assignment models should be used to keep track of what devices are assigned to which patients.

Having this separate model provides a few benefits:

It provides a way to relate subset of data and users based on time. For example, if the same user is assigned the same device multiple times over the course of a few years, the DeviceAssignment records allows analysts to distinguish between different periods of collection.

When assignment records are persisted over time persisted, it provides a log of when devices were assigned to different users.

It removes the requirement that when devices report data, they have to keep track of the user to which its assigned. With this record, the MedOps service can keep track of what device is assigned to a user and automatically associate the data when the device reports it.

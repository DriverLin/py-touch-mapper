#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <linux/input.h>

int running = 1;

int main(int argc, char *argv[]){
    int dev_num = atoi(argv[1]);
    char dev_path[80];
    sprintf(dev_path, "/dev/input/event%d", dev_num);
    printf("dev_path: %s\n", dev_path);
    int fd = open(dev_path, O_RDONLY | O_NONBLOCK);
    if (fd == -1){
        printf("Failed to open dev.\n");
        exit(1);
    }
    printf("Getting exclusive access: ");
    printf("%s\n", (ioctl(fd, EVIOCGRAB, 1) == 0) ? "SUCCESS" : "FAILURE");
    char dev_name[256] = "Unknown";
    ioctl(fd, EVIOCGNAME(sizeof(dev_name)), dev_name);
    printf("Reading From : %s \n", dev_name);
    struct input_event event;
    while (running == 1)
        if (read(fd, &event, sizeof(event)) != -1)
        {
            printf("Event: type: %d, code: %d, value: %d\n", event.type, event.code, event.value);
        }
    printf("Exiting.\n");
    close(fd);
    return 0;
}


// 偶然发现 adb shell 环境下
// 可以对/dev/input/eventX进行读取
// 并且能够获取独占访问权限
// 结合反射调用android的inputManager
// 可以在无root权限下完成映射


//uinput 虚拟设备 也是也用的

#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <linux/input.h>
#include <pthread.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>

int running = 1;

int socket_descriptor;
struct sockaddr_in address;

void initUDP(char *ip, int port)
{
    memset(&address, 0, sizeof(address));
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = inet_addr(ip); //这里不一样
    address.sin_port = htons(port);
    socket_descriptor = socket(AF_INET, SOCK_DGRAM, 0); // IPV4  SOCK_DGRAM 数据报套接字（UDP协议）
}

void atomSend(char *data, int len)
{
    sendto(socket_descriptor, data, len, 0, (struct sockaddr *)&address, sizeof(address));
}

void sendMsg(char *dev_name, char *data, int len)
{
    char buf[1024];
    char *p = buf;
    memset(buf, 0, sizeof(buf));
    memcpy(p , &len, 1);//len 一字节
    p += 1;
    memcpy(p , data, len * 8);
    p += len * 8;
    memcpy(p , dev_name, strlen(dev_name));
    atomSend(buf,strlen(dev_name) + len * 8 + 1);
}

void readThread(int dev_num)
{
    char dev_path[80];
    sprintf(dev_path, "/dev/input/event%d", dev_num);
    int fd = open(dev_path, O_RDONLY | O_NONBLOCK);
    printf("Getting exclusive access: ");
    printf("%s\n", (ioctl(fd, EVIOCGRAB, 1) == 0) ? "SUCCESS" : "FAILURE");
    
    struct input_event event;
    char buffer[1024]; // 8字节一个包 最长32个包
    int package_count = 0;
    
    char *p = buffer;
    memcpy(p , &dev_num, 1);//第一个字节是设备号
    p += 2;
    
    while (running == 1)
    {
        if (read(fd, &event, sizeof(event)) != -1)
        {
            if (event.type == 0 && event.code == 0 && event.value == 0)
            {
                p = buffer;//指针指向开头
                p++;
                memcpy(p , &package_count, 1);//第二个byte 包数
                p++;
                atomSend(buffer,package_count * 8 + 2);
                package_count = 0;//包数量清零
                // printf("\n");
            }
            else
            {
                memcpy(p, &event.type, 2);
                p += 2;
                memcpy(p, &event.code, 2);
                p += 2;
                memcpy(p, &event.value, 4);
                p += 4;
                package_count++;
                // printf("[%d %d %d]", event.type, event.code, event.value);
            }
        }
    }
    close(fd);
}

//参数一是lock文件位置
//程序会持续检查lock文件是否存在
//不存在则退出
//后面的参数为设备号
//会打开每个设备,获取独占权限,并发送事件
int main(int argc, char *argv[])
{
    if (access(argv[1], F_OK) == 0)
    {
        remove(argv[1]);
        printf("remove lock file\n");
    }
    int fd = open(argv[1], O_CREAT | O_RDWR, 0666);
    if (fd == -1)
    {
        printf("Failed to create lock file.\n");
        return 1;
    }
    else
    {
        char buffer[4096];
        memset(buffer, 0, sizeof(buffer));
        char *p = buffer;
        p += 2 ;//第一第二字节都为0 传输内容为设备名
        for (int i = 2; i < argc; i++){
            int dev_num = atoi(argv[i]);
            char dev_path[80];
            sprintf(dev_path, "/dev/input/event%d", dev_num);
            int dev_fd = open(dev_path, O_RDONLY | O_NONBLOCK);
            if (dev_fd == -1)
            {
                printf("Failed to open dev.\n");
                return -1;
            }
            char dev_name[256] = "Unknown";
            ioctl(dev_fd, EVIOCGNAME(sizeof(dev_name)), dev_name);
            printf("Reading From : %s \n", dev_name);
            
            char index_name[256 + 16];
            sprintf(index_name, "%d:%s|", dev_num, dev_name);
            
            memcpy(p, index_name, strlen(index_name));
            p += strlen(index_name);
          
            close(dev_fd);
        }
        initUDP("127.0.0.1", 9999);
        atomSend(buffer,sizeof(buffer));
        printf("Create lock file.\n");
        close(fd);
    }

    

    pthread_t threads[argc - 2];
    for (int i = 2; i < argc; i++)
    {
        int dev_num = atoi(argv[i]);
        pthread_t tid;
        pthread_create(&tid, NULL, (void *)readThread, (void *)(long)dev_num);
        threads[i - 2] = tid;
    }

    while (access(argv[1], F_OK) == 0)
    {
        usleep(100000);
    }
    running = 0;
    for (int i = 0; i < argc - 2; i++)
    {
        pthread_join(threads[i], NULL);
    }
    close(socket_descriptor);
    printf("Exiting.\n");
    return 0;
}

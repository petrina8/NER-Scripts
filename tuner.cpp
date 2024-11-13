#include <iostream>

#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <time.h>
#include <unistd.h>

#include <thread>

#include <linux/dvb/dmx.h>
#include <linux/dvb/frontend.h>

#define FRONT "/dev/dvb/adapter0/frontend0"
#define DEMUX "/dev/dvb/adapter0/demux0"

int tune(int freq) {
  int front;

  struct dtv_property propertiesArray[] = {
      {.cmd = DTV_FREQUENCY},
      {.cmd = DTV_BANDWIDTH_HZ},
      {.cmd = DTV_TUNE},
  };
  propertiesArray[0].u.data = freq;
  propertiesArray[1].u.data = 6000000;

  struct dtv_properties writeProperties {
    .num = 3, .props = propertiesArray
  };

  if ((front = open(FRONT, O_RDWR)) < 0) {
    perror("FRONTEND DEVICE: ");
    return -1;
  }

  if (ioctl(front, FE_SET_PROPERTY, &writeProperties) < 0) {
    perror("FRONTEND DEVICE: ");
    return -1;
  }
  std::cout << "frequency changed to: " << propertiesArray[0].u.data << "hz\n";

  fe_status_t stat;
  int counter = 0;
  while (1) {
    if (ioctl(front, FE_READ_STATUS, &stat) < 0) {
      perror("FE READ STATUS: ");
      return -1;
    }
    if (stat & FE_HAS_LOCK) {
      break;
    } else if (counter++ >= 5) {
      std::cout << "TIMEOUT ERROR\n";
      return -1;
    }
    std::this_thread::sleep_for(std::chrono::seconds(1));
  }
  std::cout << "Tuning OK\n";
  return 0;
}

int setFilter() {
  int demux;

  demux = open(DEMUX, O_RDWR);

  if ( demux < 0) {
    perror("DEMUX ERROR");
    return -1;
  }

  dmx_pes_filter_params pesFilterParams;
  pesFilterParams.pid = 0x2000;
  pesFilterParams.input = DMX_IN_FRONTEND;
  pesFilterParams.output = DMX_OUT_TS_TAP;
  pesFilterParams.pes_type = DMX_PES_OTHER;
  pesFilterParams.flags = DMX_IMMEDIATE_START | DMX_CHECK_CRC;

    int result = 0;
  if (result = ioctl(demux, DMX_SET_PES_FILTER, &pesFilterParams) < 0) {
    std::cout << "result:" << result << std::endl;
    perror("DEMUX ERROR");
    return -1;
  }

  return 0;
}

int main(int argc, char *argv[]) {
  if (tune(557143000) < 0) {
    std::cout << "Tunning error\n";
    return -1;
  }

  setFilter();

  while(1);

  return 0;
}

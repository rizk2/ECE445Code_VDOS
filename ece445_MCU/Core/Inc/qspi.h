/*
 * qspi.h
 *
 *  Created on: Apr 20, 2025
 *      Author: davidgong
 */

#ifndef INC_QSPI_H_
#define INC_QSPI_H_

#include "stm32wbxx_hal.h"

/*
 * 1 plane per device
 * 2048 blocks per plane
 * 64 pages per block
 * 4352 bytes per block. 4096 bytes for storage and 256 bytes for error correcting codes.
 *
 * Erasing a block sets all bytes in all pages in the block to 0xFF.
 * You can not re-program a page. Programming can only write logic 1 to logic 0. You must erase first.
 */

HAL_StatusTypeDef QSPI_readStatus(QSPI_HandleTypeDef *hqspi, uint8_t *status);
HAL_StatusTypeDef QSPI_unlockBlocks(QSPI_HandleTypeDef *hqspi);
HAL_StatusTypeDef QSPI_reset(QSPI_HandleTypeDef *hqspi);
HAL_StatusTypeDef QSPI_readID(QSPI_HandleTypeDef *hqspi, uint8_t *pdata);
HAL_StatusTypeDef QSPI_writeEnable(QSPI_HandleTypeDef *hqspi);
HAL_StatusTypeDef QSPI_program(QSPI_HandleTypeDef *hqspi, uint8_t *pdata, uint32_t addr);
HAL_StatusTypeDef QSPI_blockErase(QSPI_HandleTypeDef *hqspi, uint32_t addr);
HAL_StatusTypeDef QSPI_readPage(QSPI_HandleTypeDef *hqspi, uint8_t *pdata, uint32_t addr);

#endif /* INC_QSPI_H_ */

/*
 * qspi.c
 *
 *  Created on: Apr 20, 2025
 *      Author: davidgong
 */

#include "qspi.h"

HAL_StatusTypeDef QSPI_readStatus(QSPI_HandleTypeDef *hqspi, uint8_t* status){
	QSPI_CommandTypeDef s_command = {0};
	HAL_StatusTypeDef ret = HAL_OK;
	s_command.InstructionMode = QSPI_INSTRUCTION_1_LINE;
	s_command.Instruction = 0x0F;
	s_command.DataMode = QSPI_DATA_1_LINE;
	s_command.AddressMode = QSPI_ADDRESS_1_LINE;
	s_command.AddressSize = QSPI_ADDRESS_8_BITS;
	s_command.Address = 0xA0;
	s_command.DummyCycles = 0;
	s_command.NbData = 1;
	ret = HAL_QSPI_Command(hqspi, &s_command, HAL_QSPI_TIMEOUT_DEFAULT_VALUE);
	if(ret) return ret;
	ret = HAL_QSPI_Receive(hqspi, status, HAL_QSPI_TIMEOUT_DEFAULT_VALUE);
	if(ret) return ret;

	s_command.Address = 0xB0;
	ret = HAL_QSPI_Command(hqspi, &s_command, HAL_QSPI_TIMEOUT_DEFAULT_VALUE);
	if(ret) return ret;
	ret = HAL_QSPI_Receive(hqspi, &status[1], HAL_QSPI_TIMEOUT_DEFAULT_VALUE);
	if(ret) return ret;

	s_command.Address = 0xC0;
	ret = HAL_QSPI_Command(hqspi, &s_command, HAL_QSPI_TIMEOUT_DEFAULT_VALUE);
	if(ret) return ret;
	ret = HAL_QSPI_Receive(hqspi, &status[2], HAL_QSPI_TIMEOUT_DEFAULT_VALUE);
	return ret;
}

HAL_StatusTypeDef QSPI_unlockBlocks(QSPI_HandleTypeDef *hqspi){
	QSPI_CommandTypeDef s_command = {0};
	uint8_t data = 0;
	HAL_StatusTypeDef ret = HAL_OK;
	s_command.InstructionMode = QSPI_INSTRUCTION_1_LINE;
	s_command.Instruction = 0x1F;
	s_command.DataMode = QSPI_DATA_1_LINE;
	s_command.AddressMode = QSPI_ADDRESS_1_LINE;
	s_command.AddressSize = QSPI_ADDRESS_8_BITS;
	s_command.Address = 0xA0;
	s_command.DummyCycles = 0;
	s_command.NbData = 1;
	ret = HAL_QSPI_Command(hqspi, &s_command, HAL_QSPI_TIMEOUT_DEFAULT_VALUE);
	if(ret) return ret;
	ret = HAL_QSPI_Transmit(hqspi, &data, HAL_QSPI_TIMEOUT_DEFAULT_VALUE);
	return ret;
}

HAL_StatusTypeDef QSPI_reset(QSPI_HandleTypeDef *hqspi){
	QSPI_CommandTypeDef s_command = {0};
	s_command.InstructionMode = QSPI_INSTRUCTION_1_LINE;
	s_command.Instruction = 0xFF;
	s_command.DataMode = QSPI_DATA_NONE;
	s_command.AddressMode = QSPI_ADDRESS_NONE;
	s_command.DummyCycles = 0;
	s_command.NbData = 0;
	return HAL_QSPI_Command(hqspi, &s_command, HAL_QSPI_TIMEOUT_DEFAULT_VALUE);
}

HAL_StatusTypeDef QSPI_readID(QSPI_HandleTypeDef *hqspi, uint8_t *pdata){
	QSPI_CommandTypeDef s_command = {0};
	HAL_StatusTypeDef ret = HAL_OK;
	s_command.InstructionMode = QSPI_INSTRUCTION_1_LINE;
	s_command.Instruction = 0x9F;
	s_command.DataMode = QSPI_DATA_1_LINE;
	s_command.AddressMode = QSPI_ADDRESS_NONE;
	s_command.DummyCycles = 8;
	s_command.NbData = 2;
	ret = HAL_QSPI_Command(hqspi, &s_command, HAL_QSPI_TIMEOUT_DEFAULT_VALUE);
	if(ret) return ret;
	ret = HAL_QSPI_Receive(hqspi, pdata, HAL_QSPI_TIMEOUT_DEFAULT_VALUE);
	return ret;
}

HAL_StatusTypeDef QSPI_writeEnable(QSPI_HandleTypeDef *hqspi){
	QSPI_CommandTypeDef s_command = {0};
	s_command.InstructionMode = QSPI_INSTRUCTION_1_LINE;
	s_command.Instruction = 0x06;
	s_command.DataMode = QSPI_DATA_NONE;
	s_command.AddressMode = QSPI_ADDRESS_NONE;
	s_command.DummyCycles = 0;
	s_command.NbData = 0;
	return HAL_QSPI_Command(hqspi, &s_command, HAL_QSPI_TIMEOUT_DEFAULT_VALUE);
}

HAL_StatusTypeDef QSPI_program(QSPI_HandleTypeDef *hqspi, uint8_t *pdata, uint32_t addr){
	QSPI_CommandTypeDef s_command = {0};
	HAL_StatusTypeDef ret = HAL_OK;
	if(addr > 131072){
		return HAL_ERROR;
	}
	ret = QSPI_writeEnable(hqspi);
	if(ret) return ret;
	//Program Load x2 Random
	s_command.InstructionMode = QSPI_INSTRUCTION_1_LINE;
	s_command.Instruction = 0x44;
	s_command.DataMode = QSPI_DATA_2_LINES;
	s_command.AddressMode = QSPI_ADDRESS_1_LINE;
	s_command.AddressSize = QSPI_ADDRESS_16_BITS;
	s_command.Address = 0x00;
	s_command.DummyCycles = 0;
	s_command.NbData = 4096;
	ret = HAL_QSPI_Command(hqspi, &s_command, HAL_QSPI_TIMEOUT_DEFAULT_VALUE);
	if(ret) return ret;
	ret = HAL_QSPI_Transmit(hqspi, pdata, HAL_QSPI_TIMEOUT_DEFAULT_VALUE);
	if(ret) return ret;

	//Program Execute
	s_command.Instruction = 0x10;
	s_command.DataMode = QSPI_DATA_NONE;
	s_command.AddressSize = QSPI_ADDRESS_24_BITS;
	s_command.Address = addr;
	s_command.DummyCycles = 0;
	s_command.NbData = 0;
	return HAL_QSPI_Command(hqspi, &s_command, HAL_QSPI_TIMEOUT_DEFAULT_VALUE);
}

HAL_StatusTypeDef QSPI_blockErase(QSPI_HandleTypeDef *hqspi, uint32_t addr){
	QSPI_CommandTypeDef s_command = {0};
	HAL_StatusTypeDef ret = HAL_OK;
	if(addr >= 2048){
		return HAL_ERROR;
	}
	ret = QSPI_writeEnable(hqspi);
	if(ret) return ret;
	//Block Erase
	s_command.InstructionMode = QSPI_INSTRUCTION_1_LINE;
	s_command.Instruction = 0xD8;
	s_command.DataMode = QSPI_DATA_NONE;
	s_command.AddressMode = QSPI_ADDRESS_1_LINE;
	s_command.AddressSize = QSPI_ADDRESS_24_BITS;
	s_command.Address = addr;
	s_command.DummyCycles = 0;
	ret = HAL_QSPI_Command(hqspi, &s_command, HAL_QSPI_TIMEOUT_DEFAULT_VALUE);
	HAL_Delay(10);
	return ret;
}


HAL_StatusTypeDef QSPI_readPage(QSPI_HandleTypeDef *hqspi, uint8_t *pdata, uint32_t addr){
	QSPI_CommandTypeDef s_command = {0};
	HAL_StatusTypeDef ret = HAL_OK;
	if(addr >= 131072){
		return HAL_ERROR;
	}
	//Send Page Read Command
	s_command.InstructionMode = QSPI_INSTRUCTION_1_LINE;
	s_command.Instruction = 0x13;
	s_command.DataMode = QSPI_DATA_NONE;
	s_command.AddressMode = QSPI_ADDRESS_1_LINE;
	s_command.AddressSize = QSPI_ADDRESS_24_BITS;
	s_command.Address = addr;
	s_command.AlternateByteMode = QSPI_ALTERNATE_BYTES_NONE;
	s_command.DummyCycles = 0;
	ret = HAL_QSPI_Command(hqspi, &s_command, HAL_QSPI_TIMEOUT_DEFAULT_VALUE);
	if(ret) return ret;
	HAL_Delay(1);

	//Read from Cache x2
	s_command.InstructionMode = QSPI_INSTRUCTION_1_LINE;
	s_command.Instruction = 0x3B;
	s_command.DataMode = QSPI_DATA_2_LINES;
	s_command.AddressMode = QSPI_ADDRESS_1_LINE;
	s_command.AddressSize = QSPI_ADDRESS_16_BITS;
	s_command.Address = 0x00;
	s_command.AlternateByteMode = QSPI_ALTERNATE_BYTES_NONE;
	s_command.DummyCycles = 8;
	s_command.NbData = 4352;
	ret = HAL_QSPI_Command(hqspi, &s_command, HAL_QSPI_TIMEOUT_DEFAULT_VALUE);
	if(ret) return ret;
	return HAL_QSPI_Receive(hqspi, pdata, HAL_QSPI_TIMEOUT_DEFAULT_VALUE);
}

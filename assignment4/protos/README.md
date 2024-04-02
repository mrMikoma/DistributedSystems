
4. **Initialize proto**

   ```bash
   python3 -m grpc_tools.protoc -Iprotos --python_out=server/node --grpc_python_out=server/node protos/chat.proto
   ```
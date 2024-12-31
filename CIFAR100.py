import random

# 模拟下载进度信息
print("Downloading dataset...")
for i in range(1, 11):
    print(f"Progress: {i * 10}%")

# 模拟数据集大小
train_size = 1464
test_size = 1449
print(f"\nRead {train_size} training examples")
print(f"Read {test_size} testing examples")

# 模拟训练过程
epochs = 10
for epoch in range(1, epochs + 1):
    loss = 2.5 - epoch * 0.15 + random.uniform(-0.05, 0.05)  # 模拟损失值下降
    accuracy = 0.15 + epoch * 0.055 + random.uniform(-0.02, 0.02) # 模拟精度上升
    print(f"\nEpoch {epoch} , loss {loss:.3f}")
    print(f"Test Accuracy: {accuracy:.3f}")

# 模拟最终精度
final_accuracy = 0.7 + random.uniform(-0.02, 0.02)
print(f"\nFinal Test Accuracy: {final_accuracy:.3f}")
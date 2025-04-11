from house_gan.models import Generator
import torch

def test_model_loading():
    try:
        print("Testing model loading...")
        generator = Generator()
        checkpoint = 'exp_demo_D_500000.pth'
        print(f"Loading model from {checkpoint}")
        generator.load_state_dict(torch.load(checkpoint, map_location=torch.device('cpu')))
        print("Model loaded successfully!")
        return True
    except Exception as e:
        print(f"Error loading model: {e}")
        return False

if __name__ == "__main__":
    test_model_loading() 
import pytest
import json
import base64
from api.index import app, text_to_number, number_to_text, base64_to_number, number_to_base64


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestTextToNumber:
    """Test text to number conversion"""
    
    def test_basic_numbers(self):
        """Test basic number words"""
        assert text_to_number("one") == 1
        assert text_to_number("two") == 2
        assert text_to_number("ten") == 10
    
    def test_zero_cases(self):
        """Test zero conversion"""
        assert text_to_number("zero") == 0
        assert text_to_number("nil") == 0
    
    def test_case_insensitive(self):
        """Test case insensitive conversion"""
        assert text_to_number("ONE") == 1
        assert text_to_number("Two") == 2
        assert text_to_number("ZERO") == 0
    
    def test_invalid_text(self):
        """Test invalid text input"""
        with pytest.raises(ValueError):
            text_to_number("invalid")
        with pytest.raises(ValueError):
            text_to_number("eleven")  # Not in the basic dictionary
        with pytest.raises(ValueError):
            text_to_number("")


class TestNumberToText:
    """Test number to text conversion"""
    
    def test_basic_numbers(self):
        """Test basic number conversion"""
        assert number_to_text(1) == "one"
        assert number_to_text(42) == "forty-two"
        assert number_to_text(100) == "one hundred"
    
    def test_zero(self):
        """Test zero conversion"""
        assert number_to_text(0) == "zero"
    
    def test_negative_numbers(self):
        """Test negative number conversion"""
        assert number_to_text(-1) == "minus one"
        assert number_to_text(-42) == "minus forty-two"


class TestBase64Conversion:
    """Test base64 conversion functions"""
    
    def test_number_to_base64_basic(self):
        """Test basic number to base64 conversion"""
        # Test with a known value - 42 in little-endian should be specific base64
        result = number_to_base64(42)
        assert isinstance(result, str)
        # Verify it's valid base64
        base64.b64decode(result)
    
    def test_base64_to_number_basic(self):
        """Test basic base64 to number conversion"""
        # Create a base64 string from known bytes in little-endian
        test_bytes = (42).to_bytes(1, byteorder='little')
        test_b64 = base64.b64encode(test_bytes).decode('utf-8')
        result = base64_to_number(test_b64)
        assert result == 42
    
    def test_zero_conversion(self):
        """Test zero conversion to/from base64"""
        # This should handle the edge case where bit_length() is 0
        result = number_to_base64(0)
        assert isinstance(result, str)
        assert base64_to_number(result) == 0
    
    def test_large_numbers(self):
        """Test large number conversion"""
        large_num = 1000000
        b64_result = number_to_base64(large_num)
        assert base64_to_number(b64_result) == large_num
    
    def test_byte_order_consistency(self):
        """Test that byte order is consistent between conversion functions"""
        test_numbers = [1, 42, 255, 256, 65535, 65536]
        for num in test_numbers:
            b64_result = number_to_base64(num)
            converted_back = base64_to_number(b64_result)
            assert converted_back == num, f"Failed for number {num}"
    
    def test_little_endian_requirement(self):
        """Test that base64 conversion uses little-endian byte order"""
        # Test a multi-byte number where byte order matters
        test_num = 0x1234  # 4660 in decimal
        result = number_to_base64(test_num)
        
        # Manually create little-endian base64 for comparison
        expected_bytes = test_num.to_bytes(2, byteorder='little')
        expected_b64 = base64.b64encode(expected_bytes).decode('utf-8')
        
        # The current implementation uses big-endian (bug), so this should fail
        # After fixing, this test should pass
        assert result == expected_b64, "Base64 conversion should use little-endian byte order"
    
    def test_invalid_base64(self):
        """Test invalid base64 input"""
        with pytest.raises(ValueError):
            base64_to_number("invalid_base64!")
        # Empty string is actually valid - it represents 0
        assert base64_to_number("") == 0


class TestFlaskEndpoints:
    """Test Flask API endpoints"""
    
    def test_index_route(self, client):
        """Test the index route"""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_convert_decimal_to_binary(self, client):
        """Test decimal to binary conversion"""
        data = {
            'input': '42',
            'inputType': 'decimal',
            'outputType': 'binary'
        }
        response = client.post('/convert', json=data)
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['result'] == '101010'
        assert result['error'] is None
    
    def test_convert_binary_to_decimal(self, client):
        """Test binary to decimal conversion"""
        data = {
            'input': '101010',
            'inputType': 'binary',
            'outputType': 'decimal'
        }
        response = client.post('/convert', json=data)
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['result'] == '42'
        assert result['error'] is None
    
    def test_convert_decimal_to_hex(self, client):
        """Test decimal to hexadecimal conversion"""
        data = {
            'input': '255',
            'inputType': 'decimal',
            'outputType': 'hexadecimal'
        }
        response = client.post('/convert', json=data)
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['result'] == 'ff'
        assert result['error'] is None
    
    def test_convert_hex_to_decimal(self, client):
        """Test hexadecimal to decimal conversion"""
        data = {
            'input': 'ff',
            'inputType': 'hexadecimal',
            'outputType': 'decimal'
        }
        response = client.post('/convert', json=data)
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['result'] == '255'
        assert result['error'] is None
    
    def test_convert_decimal_to_octal(self, client):
        """Test decimal to octal conversion"""
        data = {
            'input': '64',
            'inputType': 'decimal',
            'outputType': 'octal'
        }
        response = client.post('/convert', json=data)
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['result'] == '100'
        assert result['error'] is None
    
    def test_convert_text_to_decimal(self, client):
        """Test text to decimal conversion"""
        data = {
            'input': 'five',
            'inputType': 'text',
            'outputType': 'decimal'
        }
        response = client.post('/convert', json=data)
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['result'] == '5'
        assert result['error'] is None
    
    def test_convert_decimal_to_text(self, client):
        """Test decimal to text conversion"""
        data = {
            'input': '42',
            'inputType': 'decimal',
            'outputType': 'text'
        }
        response = client.post('/convert', json=data)
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['result'] == 'forty-two'
        assert result['error'] is None
    
    def test_convert_base64_roundtrip(self, client):
        """Test base64 conversion roundtrip"""
        # Test decimal to base64 and back
        data1 = {
            'input': '42',
            'inputType': 'decimal',
            'outputType': 'base64'
        }
        response1 = client.post('/convert', json=data1)
        assert response1.status_code == 200
        result1 = json.loads(response1.data)
        assert result1['error'] is None
        
        # Convert back from base64 to decimal
        data2 = {
            'input': result1['result'],
            'inputType': 'base64',
            'outputType': 'decimal'
        }
        response2 = client.post('/convert', json=data2)
        assert response2.status_code == 200
        result2 = json.loads(response2.data)
        assert result2['result'] == '42'
        assert result2['error'] is None


class TestErrorHandling:
    """Test error handling"""
    
    def test_invalid_input_type(self, client):
        """Test invalid input type"""
        data = {
            'input': '42',
            'inputType': 'invalid',
            'outputType': 'decimal'
        }
        response = client.post('/convert', json=data)
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['result'] is None
        assert 'Invalid input type' in result['error']
    
    def test_invalid_output_type(self, client):
        """Test invalid output type"""
        data = {
            'input': '42',
            'inputType': 'decimal',
            'outputType': 'invalid'
        }
        response = client.post('/convert', json=data)
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['result'] is None
        assert 'Invalid output type' in result['error']
    
    def test_invalid_binary_input(self, client):
        """Test invalid binary input"""
        data = {
            'input': '102',  # Invalid binary (contains '2')
            'inputType': 'binary',
            'outputType': 'decimal'
        }
        response = client.post('/convert', json=data)
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['result'] is None
        assert result['error'] is not None
    
    def test_invalid_hex_input(self, client):
        """Test invalid hexadecimal input"""
        data = {
            'input': 'xyz',  # Invalid hex
            'inputType': 'hexadecimal',
            'outputType': 'decimal'
        }
        response = client.post('/convert', json=data)
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['result'] is None
        assert result['error'] is not None


class TestEdgeCases:
    """Test edge cases"""
    
    def test_zero_conversions(self, client):
        """Test zero in all formats"""
        # Test zero from decimal to all other formats
        formats = ['binary', 'octal', 'hexadecimal', 'text', 'base64']
        for output_format in formats:
            data = {
                'input': '0',
                'inputType': 'decimal',
                'outputType': output_format
            }
            response = client.post('/convert', json=data)
            assert response.status_code == 200
            result = json.loads(response.data)
            assert result['error'] is None, f"Failed for output format {output_format}"
    
    def test_large_numbers(self, client):
        """Test large number conversions"""
        large_num = '1000000'
        data = {
            'input': large_num,
            'inputType': 'decimal',
            'outputType': 'binary'
        }
        response = client.post('/convert', json=data)
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['error'] is None

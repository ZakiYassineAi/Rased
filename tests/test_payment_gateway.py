import pytest
import pytest_asyncio
from decimal import Decimal
from src.payment_gateway import AdvancedD17PaymentGateway, D17PaymentConfig

# Use pytest_asyncio.fixture for async fixtures
@pytest_asyncio.fixture
async def payment_gateway():
    config = D17PaymentConfig(
        merchant_id="test_merchant",
        api_key="test_api_key",
        secret_key="test_secret_key"
    )
    gw = AdvancedD17PaymentGateway(config)
    yield gw
    # Clean up the session after the test is done
    await gw.session.close()

@pytest.mark.asyncio
async def test_validate_payment_parameters_valid(payment_gateway):
    """
    Tests that _validate_payment_parameters runs without error for valid inputs.
    """
    try:
        payment_gateway._validate_payment_parameters(
            amount=Decimal('100.000'),
            user_id="user123",
            company_id="company456"
        )
    except ValueError:
        pytest.fail("_validate_payment_parameters raised ValueError unexpectedly!")

@pytest.mark.asyncio
async def test_validate_payment_parameters_zero_amount(payment_gateway):
    """
    Tests that a zero amount raises a ValueError.
    """
    with pytest.raises(ValueError, match="المبلغ يجب أن يكون أكبر من الصفر"):
        payment_gateway._validate_payment_parameters(
            amount=Decimal('0'),
            user_id="user123",
            company_id="company456"
        )

@pytest.mark.asyncio
async def test_validate_payment_parameters_negative_amount(payment_gateway):
    """
    Tests that a negative amount raises a ValueError.
    """
    with pytest.raises(ValueError, match="المبلغ يجب أن يكون أكبر من الصفر"):
        payment_gateway._validate_payment_parameters(
            amount=Decimal('-100.000'),
            user_id="user123",
            company_id="company456"
        )

@pytest.mark.asyncio
async def test_validate_payment_parameters_missing_user_id(payment_gateway):
    """
    Tests that a missing user_id raises a ValueError.
    """
    with pytest.raises(ValueError, match="معرف المستخدم والشركة مطلوبان"):
        payment_gateway._validate_payment_parameters(
            amount=Decimal('100.000'),
            user_id="",
            company_id="company456"
        )

@pytest.mark.asyncio
async def test_validate_payment_parameters_missing_company_id(payment_gateway):
    """
    Tests that a missing company_id raises a ValueError.
    """
    with pytest.raises(ValueError, match="معرف المستخدم والشركة مطلوبان"):
        payment_gateway._validate_payment_parameters(
            amount=Decimal('100.000'),
            user_id="user123",
            company_id=""
        )

@pytest.mark.asyncio
async def test_validate_payment_parameters_amount_too_high(payment_gateway):
    """
    Tests that an amount over 10000 raises a ValueError.
    """
    with pytest.raises(ValueError, match="المبلغ لا يمكن أن يتجاوز 10,000 دينار"):
        payment_gateway._validate_payment_parameters(
            amount=Decimal('10001.000'),
            user_id="user123",
            company_id="company456"
        )

@pytest.mark.asyncio
async def test_validate_payment_parameters_amount_at_limit(payment_gateway):
    """
    Tests that an amount of exactly 10000 does not raise an error.
    """
    try:
        payment_gateway._validate_payment_parameters(
            amount=Decimal('10000.000'),
            user_id="user123",
            company_id="company456"
        )
    except ValueError:
        pytest.fail("_validate_payment_parameters raised ValueError unexpectedly for amount at the limit!")

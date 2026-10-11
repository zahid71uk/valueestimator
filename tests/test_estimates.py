def valid_house():
    return {
        "square_footage": 1550,
        "bedrooms": 3,
        "bathrooms": 2,
        "year_built": 1997,
        "lot_size": 6800,
        "distance_to_city_center": 4.1,
        "school_rating": 7.6,
    }


def test_single_estimate_returns_price(client):
    response = client.post("/api/v1/estimates", json=valid_house())

    assert response.status_code == 200
    assert response.json() == {"predicted_price": 325000.0}


def test_batch_estimate_returns_ordered_predictions(client):
    response = client.post(
        "/api/v1/estimates/batch",
        json={"houses": [valid_house(), valid_house()]},
    )

    assert response.status_code == 200
    assert response.json() == {
        "predictions": [325000.0, 335000.0],
        "count": 2,
    }


def test_invalid_house_reports_field_and_expected_type(client):
    house = valid_house()
    house["bedrooms"] = "three"

    response = client.post("/api/v1/estimates", json=house)

    assert response.status_code == 422
    body = response.json()
    assert body["errors"][0]["field"] == "bedrooms"
    bedrooms = next(
        field for field in body["expected"]["fields"] if field["name"] == "bedrooms"
    )
    assert bedrooms["type"] == "integer"


def test_batch_error_reports_nested_field(client):
    house = valid_house()
    house["school_rating"] = 12

    response = client.post("/api/v1/estimates/batch", json={"houses": [house]})

    assert response.status_code == 422
    assert response.json()["errors"][0]["field"] == "houses[0].school_rating"


def test_batch_rejects_more_than_one_hundred_properties(client):
    response = client.post(
        "/api/v1/estimates/batch",
        json={"houses": [valid_house()] * 101},
    )

    assert response.status_code == 422
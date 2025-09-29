API Documentation
=================

Trunk Player provides a RESTful API for accessing radio transmission data, talkgroups, and user-specific information. As of version 0.1.5, all API endpoints require authentication and filter data based on user permissions.

Authentication
--------------

All API endpoints require user authentication. Anonymous access is controlled by the ``ALLOW_ANONYMOUS`` setting.

**Authentication Methods:**

- Session authentication (web interface)
- Token authentication (for external applications)

**Headers:**

.. code-block:: http

    Authorization: Token your_token_here
    Content-Type: application/json

Core Endpoints
--------------

Transmissions
~~~~~~~~~~~~~

``GET /api_v1/transmission/``

Returns radio transmissions filtered by user's accessible talkgroups.

**Parameters:**

- ``page``: Page number for pagination
- ``page_size``: Number of results per page (default: 50)
- ``ordering``: Sort order (``-start_datetime`` for newest first)

**Response:**

.. code-block:: json

    {
        "count": 1250,
        "next": "http://example.com/api_v1/transmission/?page=2",
        "previous": null,
        "results": [
            {
                "pk": 12345,
                "start_datetime": "2024-01-15T14:30:00Z",
                "local_start_datetime": "Jan 15, 2024 2:30 PM",
                "audio_file": "http://example.com/audio/path.mp3",
                "talkgroup": 12345,
                "talkgroup_info": {
                    "url": "http://example.com/api_v1/talkgroups/123/",
                    "dec_id": 12345,
                    "alpha_tag": "POLICE_DISPATCH",
                    "description": "Police Dispatch",
                    "slug": "sys1-police-dispatch"
                },
                "freq": 460125000,
                "emergency": false,
                "units": [
                    {
                        "pk": 1,
                        "dec_id": 101,
                        "description": "Unit 101"
                    }
                ],
                "play_length": 12.5,
                "print_play_length": "00:12",
                "slug": "550e8400-e29b-41d4-a716-446655440000",
                "freq_mhz": "460.125",
                "tg_name": "POLICE_DISPATCH",
                "source": 1,
                "audio_url": "http://example.com/audio/path.mp3",
                "system": 1,
                "audio_file_type": "mp3"
            }
        ]
    }

Talkgroups
~~~~~~~~~~

``GET /api_v1/talkgroups/``

Returns talkgroups the authenticated user has access to.

**Response:**

.. code-block:: json

    {
        "count": 45,
        "next": null,
        "previous": null,
        "results": [
            {
                "url": "http://example.com/api_v1/talkgroups/123/",
                "dec_id": 12345,
                "alpha_tag": "POLICE_DISPATCH",
                "description": "Police Dispatch Channel",
                "slug": "sys1-police-dispatch"
            }
        ]
    }

User-Specific Endpoints
-----------------------

Menu Talkgroups
~~~~~~~~~~~~~~~

``GET /api_v1/menutalkgrouplist/``

Returns talkgroups flagged for the user's personal menu, ordered by preference.

**Response:**

.. code-block:: json

    {
        "count": 8,
        "next": null,
        "previous": null,
        "results": [
            {
                "pk": 1,
                "name": 12345,
                "tg_name": "POLICE_DISPATCH",
                "tg_slug": "sys1-police-dispatch",
                "show_in_menu": true,
                "order": 1
            }
        ]
    }

User Scan Lists
~~~~~~~~~~~~~~~

``GET /api_v1/menuscanlist/``

Returns the user's active scan lists.

**Response:**

.. code-block:: json

    {
        "count": 3,
        "next": null,
        "previous": null,
        "results": [
            {
                "pk": 1,
                "name": 1,
                "scan_name": "Emergency Services",
                "scan_description": "Emergency Services",
                "scan_slug": "user5-emergency-services"
            }
        ]
    }

Transmission Filtering
~~~~~~~~~~~~~~~~~~~~~~

``GET /api_v1/scan/<slug>/``

Returns transmissions filtered by scan list or special keywords.

**Parameters:**

- ``<slug>``: Scan list slug or special keywords:

  - ``default``: User's default scan list or all accessible talkgroups
  - ``user5-emergency-services``: Specific user scan list
  - ``public-scan-name``: Public scan list

**Response:** Same format as ``/api_v1/transmission/`` but filtered by scan list talkgroups.

Unit and Talkgroup Filtering
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``GET /api_v1/tg/<filter_val>/``

Returns transmissions filtered by talkgroup criteria.

``GET /api_v1/unit/<filter_val>/``

Returns transmissions filtered by unit criteria.

**Parameters:**

- ``<filter_val>``: Plus-separated search terms (e.g., ``police+dispatch``)

Error Responses
---------------

Authentication Required
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: json

    {
        "detail": "Authentication credentials were not provided."
    }

HTTP Status: ``401 Unauthorized``

Permission Denied
~~~~~~~~~~~~~~~~~

.. code-block:: json

    {
        "detail": "You do not have permission to perform this action."
    }

HTTP Status: ``403 Forbidden``

Not Found
~~~~~~~~~

.. code-block:: json

    {
        "detail": "Not found."
    }

HTTP Status: ``404 Not Found``

Rate Limiting
-------------

API endpoints may be rate-limited to prevent abuse:

- **Rate**: 100 requests per minute per user
- **Headers**: Rate limit information included in response headers

.. code-block:: http

    X-RateLimit-Limit: 100
    X-RateLimit-Remaining: 85
    X-RateLimit-Reset: 1641916800

Integration Examples
--------------------

Python
~~~~~~

.. code-block:: python

    import requests

    # Authentication
    headers = {
        'Authorization': 'Token your_token_here',
        'Content-Type': 'application/json'
    }

    # Get user's accessible talkgroups
    response = requests.get(
        'https://your-server.com/api_v1/talkgroups/',
        headers=headers
    )
    talkgroups = response.json()

    # Get recent transmissions
    response = requests.get(
        'https://your-server.com/api_v1/transmission/',
        headers=headers,
        params={'ordering': '-start_datetime', 'page_size': 20}
    )
    transmissions = response.json()

JavaScript
~~~~~~~~~~

.. code-block:: javascript

    // Using fetch API
    const headers = {
        'Authorization': 'Token your_token_here',
        'Content-Type': 'application/json'
    };

    // Get user's scan lists
    fetch('/api_v1/menuscanlist/', { headers })
        .then(response => response.json())
        .then(data => {
            console.log('User scan lists:', data.results);
        });

    // Get transmissions from specific scan list
    fetch('/api_v1/scan/user5-emergency-services/', { headers })
        .then(response => response.json())
        .then(data => {
            console.log('Scan list transmissions:', data.results);
        });

cURL
~~~~

.. code-block:: bash

    # Get accessible talkgroups
    curl -H "Authorization: Token your_token_here" \\
         https://your-server.com/api_v1/talkgroups/

    # Get user's menu talkgroups
    curl -H "Authorization: Token your_token_here" \\
         https://your-server.com/api_v1/menutalkgrouplist/

Migration from v0.1.4
----------------------

API Breaking Changes
~~~~~~~~~~~~~~~~~~~~

- **Authentication Required**: All endpoints now require authentication
- **Filtered Results**: Data is filtered by user permissions
- **New Endpoints**: User-specific endpoints added
- **Slug Format**: TalkGroup slugs now include system prefix

**Migration Steps:**

1. **Add Authentication**: Update API clients to include authentication headers
2. **Handle Filtering**: Expect filtered results based on user access
3. **Update Slugs**: Account for new slug format (``sys1-talkgroup-name``)
4. **New Features**: Utilize new user-specific endpoints

Best Practices
--------------

Performance
~~~~~~~~~~~

- Use pagination for large result sets
- Cache frequently accessed data
- Implement proper error handling
- Use appropriate page sizes

Security
~~~~~~~~

- Store API tokens securely
- Use HTTPS for all API communications
- Implement proper access controls
- Regular token rotation

Data Handling
~~~~~~~~~~~~~

- Respect rate limits
- Handle authentication errors gracefully
- Validate user permissions before displaying data
- Use efficient filtering and ordering
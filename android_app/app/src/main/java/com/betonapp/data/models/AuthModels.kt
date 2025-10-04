package com.betonapp.data.models

import com.google.gson.annotations.SerializedName

/**
 * Modèles de données pour l'authentification
 */

data class LoginRequest(
    val username: String,
    val password: String
)

data class LoginResponse(
    val access: String,
    val refresh: String
)

data class RefreshTokenRequest(
    val refresh: String
)

data class RefreshTokenResponse(
    val access: String
)

data class User(
    val id: Int,
    val username: String,
    val email: String,
    @SerializedName("first_name")
    val firstName: String,
    @SerializedName("last_name")
    val lastName: String,
    @SerializedName("is_staff")
    val isStaff: Boolean,
    @SerializedName("is_active")
    val isActive: Boolean,
    @SerializedName("date_joined")
    val dateJoined: String
)
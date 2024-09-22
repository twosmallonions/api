package com.twosmallonions.api;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.oauth2.core.DelegatingOAuth2TokenValidator;
import org.springframework.security.oauth2.core.OAuth2TokenValidator;
import org.springframework.security.oauth2.jwt.*;
import org.springframework.security.web.SecurityFilterChain;

import java.time.Duration;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;

@Configuration
@EnableWebSecurity
public class SecurityConfiguration {
    @Value("${spring.security.oauth2.resourceserver.jwt.issuer-uri}")
    String issuerUri;
    @Value("${spring.security.oauth2.resourceserver.jwt.audiences}")
    HashSet<String> audiences;

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
                .sessionManagement((session) -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .authorizeHttpRequests(authorize ->
                        authorize
                                .requestMatchers("/swagger-ui.html", "/swagger-ui/**", "/v3/api-docs/**").permitAll()
                                .requestMatchers("/actuator/**").permitAll()
                                .anyRequest().authenticated())
                .oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults()));

        return http.build();
    }

    private OAuth2TokenValidator<Jwt> emailVerifiedValidator() {
        String EMAIL_VERIFIED_CLAIM = "email_verified";
        return new JwtClaimValidator<Boolean>(EMAIL_VERIFIED_CLAIM, verified -> verified);
    }

    private OAuth2TokenValidator<Jwt> audienceValidator() {
        String AUD_CLAIM = "aud";
        return new JwtClaimValidator<ArrayList<String>>(AUD_CLAIM, aud -> aud.containsAll(this.audiences));
    }

    @Bean
    JwtDecoder jwtDecoder() {
            NimbusJwtDecoder jwtDecoder = JwtDecoders.fromIssuerLocation(issuerUri);

            var emailVerifiedValidator = emailVerifiedValidator();
            var withIssuer = JwtValidators.createDefaultWithIssuer(issuerUri);
            var withTimestamp = new JwtTimestampValidator(Duration.ofSeconds(5));
            var audienceValidator = audienceValidator();

            var validator = new DelegatingOAuth2TokenValidator<>(withIssuer, emailVerifiedValidator, withTimestamp, audienceValidator);

            jwtDecoder.setJwtValidator(validator);

            return jwtDecoder;
    }
}

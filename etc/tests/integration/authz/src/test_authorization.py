import os
import unittest
import time
import requests
import pytest
import json
import random


@pytest.mark.usefixtures("setup")
class TestAuthorization():
    
    def test_internal_server_error_500_candig_server_authorization_permission(self):
        body = { "input" : { "kcToken": "...", "vaultToken": "...", "authZjwks": "..." } }
        response = requests.request('POST', self.candig_server_authz_url, json=body)

        assert response.status_code == 500
    

    def test_cannot_get_candig_server_authorization_permission(self):
        body = { "input" : { "kcToken": "abc.123.123456", "vaultToken": "def.456.def456", "authZjwks": "ghi789"} }
        response = requests.request('POST', self.candig_server_authz_url, json=body)

        assert response.status_code == 500
    

    def test_can_get_candig_server_authorization_permission(self):
        body = { 
            "input" : {
                "kcToken": "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJUbEpoU1AyTURES3F0M0pyTmtrb3hYRVBrNGQ4NmlJaXVJTnZPc0Y5Q0lRIn0.eyJleHAiOjE2MDQ0MTk5MjMsImlhdCI6MTYwNDQxOTYyMywiYXV0aF90aW1lIjoxNjA0NDE5NjIzLCJqdGkiOiJjNmFhOTIyZi0zN2FiLTQ1MWYtYmFkYS0wMDYyZjQyZTc4OWEiLCJpc3MiOiJodHRwOi8vY2FuZGlnYXV0aC5sb2NhbDo4MDgxL2F1dGgvcmVhbG1zL2NhbmRpZyIsImF1ZCI6ImNxX2NhbmRpZyIsInN1YiI6ImU3MmUyY2FmLTczODMtNDA5YS04ZDdlLTAwYzk4MmI2YjExYSIsInR5cCI6IklEIiwiYXpwIjoiY3FfY2FuZGlnIiwic2Vzc2lvbl9zdGF0ZSI6IjYwNDMzNTk3LWU5NzMtNDNiMC1iZTNlLWY1NmQ3NjE2OThjYyIsImFjciI6IjEiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsInByZWZlcnJlZF91c2VybmFtZSI6ImJvYiJ9.H9NJXZwJPq579uEUVc5DHhvTvA_bhScU2yB4ZyRoao_8TWB54u4YBc1hUME5OX9excff_U_qH6FPH0lePIs3fIi0l4JaAK-c-yRWtHX3ZMwbSnr411sx9Zu1ricY3Mqx4-bHdS5XFPclFQ-encXiH2VIP3nWnoQRMa9HswJniD0_jxk-NE26Mk-v1SlIzkTY7fBqI1wKm7aOClk5t9a_YEvAwlz-7mkyYDwGHXpUpHfsga-qspOotpAtzLXEXP-66VmJyMef5oQtwkvw3k49cgb9qbikP7rxajT_jLCnKMkFiE3p03Bir-5RfBd_6NxCfeGPjiCfxMtJN3OMpHAypg", 
                "vaultToken": "eyJhbGciOiJSUzI1NiIsImtpZCI6ImUwMzE0MmM3LTZhYjAtNTk2OC03ODQ2LTc3ODQ2NjU1MWQ5YSJ9.eyJhdWQiOiJjcV9jYW5kaWciLCJleHAiOjE2MDQ1MDYwMjYsImlhdCI6MTYwNDQxOTYyNiwiaXNzIjoiL3YxL2lkZW50aXR5L29pZGMiLCJuYW1lc3BhY2UiOiJyb290IiwicGVybWlzc2lvbnMiOnsiZGF0YXNldDEyMyI6IjQifSwic3ViIjoiNDBiZDM2MWItZjM2ZC04YTQ4LTMyNzYtMzUwYzNlODIyNmJhIn0.HjtJJZF6w_A6pJkySVW2f0TBMlpDwyOOxXlWJyzutwqxHbpPfa_TyNITSag2zn86rKgWeiZbrDcjhZdDj8e0QJ6WVyqKDUquXUbVJnJjeC8zK_sb-Q2oP9r8-pYJaYFV-oqVIfy0cz-05adt7Jd-b5b9RFDXVH4k3MvV9Dybs9KfRjUqu5q3k3zAeq6MkjP63ovZYjZ7h23U_MbPbZFWV_MprLS2Mrdg7TAKTSeCuVVKlipX2XdI9uu88ejKr-Zk0a60oIjyKroLlySStFEUvODCtHiksSx-8dMFVT7uEG2GtkN2i-nYLKy3D9PN4Xf5jsH0fzFg5QrNn7105c6mlQ", 
                "authZjwks":"{\"keys\": [{\"use\": \"sig\", \"kty\": \"RSA\", \"kid\": \"e03142c7-6ab0-5968-7846-778466551d9a\", \"alg\": \"RS256\", \"n\": \"t9tlyT70cpQ4lTe5m3UoViNhhfX6FzawBpuAEx-ONgn4ZYNbryGa6PS59bIR7n_b2cN_gtJk-jhO1Gs-ItlrGNZt5SME4XKygeOKBDChfG7UOUc9JyNnZmvZldXk305yqzphJdoFaSqnYJhl91NIaEfX1ZCOElLv7H_LGzkGmGiXBuSZtoXXNGLyEnueuxDlCxvVm-XvvYbmP-L56CnFczuLzagd4jB7fKbKYbcwq3bmSlQn1CQ2nUykn_c95WC-Xhn5iyV4ZgkT3k8dRDaIwdcRcrFiCW2Ny025sMJg95GtT7ibPG_dHvSoCozNxutliqTYWs3PqRs6yQCnvKb_gQ\", \"e\": \"AQAB\"}]}"
             }
        }
        response = requests.request('POST', self.candig_server_authz_url, json=body)

        assert response.status_code == 200


    # def test_get_candig_server_authorization_does_defend_against_hs256_alg_token_tampering(self):
    #     # TODO: test HS256 attack against RS256
    #     body = { 
    #         "input" : {
    #             "kcToken": "",
    #             "vaultToken": ""
    #          }
    #     }
    #     response = requests.request('POST', self.candig_server_authz_url, json=body)

    #     assert response.status_code in [400, 500]


    # def test_get_candig_server_authorization_does_defend_against_none_alg_token_tampering(self):
    #     # TODO: test "none alg"
    #     body = { 
    #         "input" : {
    #             "kcToken": "",
    #             "vaultToken": ""
    #          }
    #     }
    #     response = requests.request('POST', self.candig_server_authz_url, json=body)

    #     assert response.status_code in [400, 500]


    def test_get_candig_server_authorization_does_defend_against_jibberish_bruteforce(self):

        start = time.time()         # the variable that holds the starting time
        elapsed = 0                 # the variable that holds the number of seconds elapsed.
        limit_sec=3

        while elapsed < limit_sec : # only run for the limited number of seconds

            # create jibberish
            j1hash1 = random.getrandbits(random.randint(256,512))
            j1hash2 = random.getrandbits(random.randint(256,512))
            j1hash3 = random.getrandbits(random.randint(256,512))
            j2hash1 = random.getrandbits(random.randint(256,512))
            j2hash2 = random.getrandbits(random.randint(256,512))
            j2hash3 = random.getrandbits(random.randint(256,512))


            jib1=("%032x" % j1hash1) + "." + ("%032x" % j1hash2) + "." + ("%032x" % j1hash3)
            jib2=("%032x" % j2hash1) + "." + ("%032x" % j2hash2) + "." + ("%032x" % j2hash3)
            # generates things like :
            # 1efda8374250e[...]6aaff58d9f1c4f2.7f1913e3c0ea281fe6[...]06c123cb6133efb121f9e.45b916cbd5eca17[...]504ef991f00266ddeff
            # to immitate a jwt format         #                                            #

            jib3 = ("%032x" % random.getrandbits(random.randint(256,512)))

            body = { 
                "input" : {
                    "kcToken": jib1,
                    "vaultToken": jib2,
                    "authZjwks": jib3
                }
            }
            response = requests.request('POST', self.candig_server_authz_url, json=body)

            assert response.status_code in [400, 500]        
            
            elapsed = time.time() - start # update the time elapsed

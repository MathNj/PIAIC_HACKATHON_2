# SSL/HTTPS Setup for testservers.online

## ✅ What Has Been Configured

### 1. **nginx-ingress Controller** (Installed)
- Acts as a load balancer and reverse proxy for your Kubernetes cluster
- Handles incoming HTTP/HTTPS traffic
- External IP: **146.190.8.222**
- Ports: 80 (HTTP), 443 (HTTPS)

### 2. **cert-manager** (Installed)
- Kubernetes-native certificate management
- Automatically provisions and renews SSL certificates from Let's Encrypt
- Monitors certificates and renews before expiration

### 3. **Let's Encrypt ClusterIssuer** (Created)
- Configured to issue free SSL certificates
- Using Let's Encrypt production server
- Contact email: admin@testservers.online
- File: `letsencrypt-issuer.yaml`

### 4. **Ingress Resource** (Created)
- Routes traffic from testservers.online → frontend-service
- Automatically provisions SSL certificate via cert-manager
- Forces HTTPS redirect (HTTP → HTTPS)
- Supports both `testservers.online` and `www.testservers.online`
- File: `frontend-ingress.yaml`

---

## 🔧 Required Action: Update DNS Records

**IMPORTANT:** Your DNS must point to the new ingress controller IP for SSL to work.

### Current DNS Configuration
- **Domain:** testservers.online
- **Current IP:** 144.126.255.56 (old frontend LoadBalancer)
- **Required IP:** **146.190.8.222** (new nginx-ingress controller)

### DNS Update Steps

1. **Login to your DNS provider** (where you registered testservers.online)

2. **Update A records:**

   | Type | Name | Value | TTL |
   |------|------|-------|-----|
   | A | @ | 146.190.8.222 | 300 |
   | A | www | 146.190.8.222 | 300 |

3. **Wait for DNS propagation** (5-30 minutes)
   - Check DNS status: `nslookup testservers.online`
   - Should return: 146.190.8.222

4. **Verify certificate issuance:**
   ```bash
   kubectl get certificate -n default
   ```
   - Wait until `READY` shows `True`
   - This can take 2-5 minutes after DNS propagates

---

## 📋 Verification Steps

### 1. Check DNS Propagation
```bash
# Windows
nslookup testservers.online

# Should return:
# Address: 146.190.8.222
```

### 2. Check Certificate Status
```bash
kubectl get certificate testservers-online-tls -n default

# Expected output when ready:
# NAME                     READY   SECRET                   AGE
# testservers-online-tls   True    testservers-online-tls   5m
```

### 3. Check Certificate Details
```bash
kubectl describe certificate testservers-online-tls -n default

# Look for:
# Status:
#   Conditions:
#     Type:    Ready
#     Status:  True
```

### 4. Test HTTPS Access
Once certificate is ready:
```bash
# Test HTTP redirect to HTTPS
curl -I http://testservers.online

# Should return:
# HTTP/1.1 308 Permanent Redirect
# Location: https://testservers.online/

# Test HTTPS
curl -I https://testservers.online

# Should return:
# HTTP/2 200
```

### 5. Open in Browser
- Visit: https://testservers.online
- Check for padlock icon 🔒
- Certificate should show: "Let's Encrypt Authority X3"

---

## 🔍 Troubleshooting

### Certificate Stuck in "Pending" State
```bash
# Check challenges
kubectl get challenges -n default

# Check challenge details
kubectl describe challenge <challenge-name> -n default

# Common issue: DNS not updated
# Solution: Verify DNS points to 146.190.8.222
```

### Certificate Shows "Failed"
```bash
# Check certificate events
kubectl describe certificate testservers-online-tls -n default

# Check issuer
kubectl describe clusterissuer letsencrypt-prod

# Delete and recreate certificate if needed
kubectl delete certificate testservers-online-tls -n default
kubectl delete ingress frontend-ingress -n default
kubectl apply -f k8s-ssl/frontend-ingress.yaml
```

### "Connection Refused" or "Cannot Reach Site"
1. Verify ingress controller is running:
   ```bash
   kubectl get pods -n ingress-nginx
   ```

2. Check ingress controller service has external IP:
   ```bash
   kubectl get svc -n ingress-nginx
   ```

3. Verify DNS points to correct IP:
   ```bash
   nslookup testservers.online
   ```

---

## 📁 Configuration Files

### `letsencrypt-issuer.yaml`
- Defines Let's Encrypt certificate issuer
- Uses ACME HTTP-01 challenge
- Production server (rate-limited, but trusted)

### `frontend-ingress.yaml`
- Routes testservers.online → frontend-service
- Automatically provisions SSL via cert-manager
- Forces HTTPS redirect
- Handles both apex and www subdomain

---

## 🔄 Certificate Renewal

**Good news:** cert-manager handles this automatically!

- Certificates are valid for 90 days
- cert-manager renews 30 days before expiration
- No manual intervention required
- Check renewal status: `kubectl get certificate -n default`

---

## 🌐 Architecture Overview

```
Internet (HTTPS)
    ↓
testservers.online:443 → DNS → 146.190.8.222
    ↓
nginx-ingress-controller (LoadBalancer)
    ↓
frontend-ingress (Ingress)
    ↓ (with TLS cert from cert-manager)
frontend-service:80 (ClusterIP)
    ↓
frontend-pod (Next.js app)
```

---

## ✅ Post-DNS Update Checklist

Once you update DNS to 146.190.8.222:

- [ ] DNS propagated (nslookup shows 146.190.8.222)
- [ ] Certificate status shows READY=True
- [ ] https://testservers.online loads with padlock
- [ ] http://testservers.online redirects to HTTPS
- [ ] www.testservers.online works
- [ ] Dashboard accessible at https://testservers.online/dashboard

---

## 🎉 Success Indicators

When everything is working:

1. ✅ Browser shows padlock icon (🔒)
2. ✅ Certificate issued by "Let's Encrypt"
3. ✅ HTTP automatically redirects to HTTPS
4. ✅ No certificate warnings
5. ✅ Dashboard loads at https://testservers.online/dashboard

---

## 📞 Support Commands

```bash
# View all Kubernetes resources
kubectl get all -n default
kubectl get all -n ingress-nginx
kubectl get all -n cert-manager

# View certificates
kubectl get certificate,certificaterequest,order,challenge -n default

# View ingress
kubectl get ingress -n default
kubectl describe ingress frontend-ingress -n default

# View logs
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller
kubectl logs -n cert-manager deployment/cert-manager

# Force certificate renewal (if needed)
kubectl delete secret testservers-online-tls -n default
# Certificate will be automatically recreated
```

---

## 🚀 Next Steps

After SSL is working:

1. **Update frontend environment variables** to use HTTPS URLs
2. **Test all features** on HTTPS
3. **Configure backend API** with HTTPS if needed
4. **Update GitHub repository** with SSL setup documentation
5. **Create demo video** showing HTTPS working

---

**Estimated Time to Complete:** 5-10 minutes after DNS update

**Questions?** Check certificate status with: `kubectl describe certificate testservers-online-tls -n default`

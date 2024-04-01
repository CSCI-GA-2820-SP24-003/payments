const PAYMENT_METHOD_TYPE = {
  PAYPAL: "PAYPAL",
  CREDIT_CARD: "CREDIT_CARD",
};

const NOTIFICATION_CLOSE_DELAY = 5000; // 5 seconds for notifications to close

class Notifications {
  static counter = 0;

  static show({ type, message }) {
    if (type !== "error" && type !== "success") {
      throw new Error("Incorrect notification type passed");
    }

    const notificationContainer = document.getElementById(
      "notification-container"
    );

    const currentId = `${type}-notification-${++this.counter}`;

    notificationContainer.innerHTML += `<div class='notification ${type}' id='${currentId}'>${message}</div>`;

    setTimeout(() => {
      notificationContainer.removeChild(document.getElementById(currentId));
    }, NOTIFICATION_CLOSE_DELAY);
  }
}

function setupModal() {
  const NONE = "none";
  const FLEX = "flex";

  const dialog = document.querySelector("dialog");
  const dialogBackdrop = document.getElementById("dialog-backdrop");
  const closeDialogButton = document.getElementById("close-dialog");
  const dialogForm = document.getElementById("dialog-form");

  const dialogFormPayPalFields = document.getElementById(
    "dialog-form-paypal-fields"
  );

  const dialogFormCreditCardFields = document.getElementById(
    "dialog-form-credit-card-fields"
  );

  function open({ title, submitButtonText, onSubmit }) {
    document.getElementById("dialog-title").textContent = title;

    const submitButton = document.getElementById("dialog-form-submit");
    submitButton.textContent = submitButtonText;
    submitButton.addEventListener("click", (event) => {
      event.preventDefault();
      onSubmit();
    });

    dialogBackdrop.style.display = "block";
    dialog.show();
  }

  function close() {
    dialogForm.reset();
    dialog.close();
    dialogBackdrop.style.display = NONE;
    dialogFormPayPalFields.style.display = FLEX;
    dialogFormCreditCardFields.style.display = NONE;
  }

  function handlePaymentMethodTypeChange(event) {
    const isPayPalTypeSelected =
      event.target.value === PAYMENT_METHOD_TYPE.PAYPAL;

    dialogFormPayPalFields.style.display = isPayPalTypeSelected ? FLEX : NONE;
    dialogFormCreditCardFields.style.display = isPayPalTypeSelected
      ? NONE
      : FLEX;
  }

  // force reset the form so that the information is not persisted after reload
  window.addEventListener("beforeunload", () => dialogForm.reset());

  document
    .getElementById("dialog-form-type")
    .addEventListener("change", handlePaymentMethodTypeChange);

  closeDialogButton.addEventListener("click", () => close());

  return {
    open,
    close,
  };
}

const modal = setupModal();

function openCreateNewPaymentMethodModal() {
  modal.open({
    title: "Create New Payment Method",
    submitButtonText: "Create",
    onSubmit: () => {
      Notifications.show({
        type: "success",
        message: "Added a new payment method!",
      });
    },
  });
}

document
  .getElementById("create-new-payment-method")
  .addEventListener("click", openCreateNewPaymentMethodModal);

// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//SSF2Target

package 
{
    public class SSF2Target extends SSF2GameObject 
    {

        public function SSF2Target(_arg_1:*):void
        {
            super(_arg_1);
        }

        override public function getType():String
        {
            return ("SSF2Target");
        }

        override public function inState(_arg_1:uint):Boolean
        {
            if (isDisposed())
            {
                SSF2API.print((("Warning: API attempted to check inState(TState." + TState.toString(_arg_1)) + ") after object has been disposed!"));
                return (_arg_1 === 2);
            };
            return (super.inState(_arg_1));
        }

        override public function setState(_arg_1:uint):void
        {
            if ((_arg_1 === 2))
            {
                SSF2API.print("Warning: Cannot explicitly set SSF2Target to DEAD state. Please use destroy() method instead.");
            };
            super.setState(_arg_1);
        }

        public function breakTarget():void
        {
            _api.breakTarget();
        }

        public function destroy():void
        {
            _api.destroy();
        }

        public function addMovement(_arg_1:Object):void
        {
            _api.addMovement(_arg_1);
        }

        public function clearMovement():void
        {
            _api.clearMovement();
        }

        public function setHurtInterrupt(_arg_1:Function):void
        {
            _api.setHurtInterrupt(_arg_1);
        }


    }
}//package 


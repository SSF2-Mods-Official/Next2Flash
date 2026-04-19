// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//SSF2Camera

package 
{
    import flash.display.MovieClip;
    import flash.geom.Point;

    public class SSF2Camera extends SSF2BaseAPIObject 
    {

        public function SSF2Camera(_arg_1:*):void
        {
            super(_arg_1);
        }

        override public function getType():String
        {
            return ("SSF2Camera");
        }

        public function getCameraParameter(_arg_1:String):*
        {
            return (_api.getCameraParameter(_arg_1));
        }

        public function updateCameraParameters(_arg_1:Object):void
        {
            _api.updateCameraParameters(_arg_1);
        }

        public function addTarget(_arg_1:MovieClip):void
        {
            _api.addTarget(_arg_1);
        }

        public function deleteTarget(_arg_1:MovieClip):void
        {
            _api.deleteTarget(_arg_1);
        }

        public function getTopLeftPoint():Point
        {
            return (_api.getTopLeftPoint());
        }

        public function getMC():MovieClip
        {
            return (_api.getMC());
        }

        public function darken():void
        {
            _api.darken();
        }

        public function killDarkener(_arg_1:Boolean=false):void
        {
            _api.killDarkener(_arg_1);
        }

        public function addTimedTarget(_arg_1:MovieClip, _arg_2:int):void
        {
            _api.addTimedCameraTarget(_arg_1, _arg_2);
        }

        public function deleteTimedCameraTarget(_arg_1:MovieClip):void
        {
            _api.deleteTimedCameraTarget(_arg_1);
        }

        public function addTimedTargetPoint(_arg_1:Point, _arg_2:int):void
        {
            _api.addTimedTargetPoint(_arg_1, _arg_2);
        }

        public function deleteTimedTargetPoint(_arg_1:Point):void
        {
            _api.deleteTimedTargetPoint(_arg_1);
        }

        public function addForcedTarget(_arg_1:MovieClip):void
        {
            _api.addForcedTarget(_arg_1);
        }

        public function deleteForcedTarget(_arg_1:MovieClip):void
        {
            _api.deleteForcedTarget(_arg_1);
        }

        public function lightFlash(_arg_1:Boolean=true):void
        {
            _api.lightFlash(_arg_1);
        }

        public function setStageFocus(_arg_1:int):void
        {
            _api.setStageFocus(_arg_1);
        }

        public function removeStageFocus():void
        {
            _api.removeStageFocus();
        }

        public function shake(_arg_1:int):void
        {
            _api.shake(_arg_1);
        }

        public function getMode():int
        {
            return (_api.getMode());
        }

        public function setMode(_arg_1:int):void
        {
            _api.setMode(_arg_1);
        }


    }
}//package 


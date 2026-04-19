// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//SSF2Stage

package 
{
    import flash.display.MovieClip;
    import flash.display.DisplayObject;
    import flash.geom.Point;

    public class SSF2Stage extends SSF2BaseAPIObject 
    {

        public function SSF2Stage(_arg_1:*):void
        {
            super(_arg_1);
        }

        override public function getType():String
        {
            return ("SSF2Stage");
        }

        public function getForeground():MovieClip
        {
            return (_api.getForeground());
        }

        public function getMidground():MovieClip
        {
            return (_api.getMidground());
        }

        public function getBackground():MovieClip
        {
            return (_api.getBackground());
        }

        public function getCameraBackgrounds():Array
        {
            return (_api.getCameraBackgrounds());
        }

        public function getWeatherMC():MovieClip
        {
            return (_api.getWeatherMC());
        }

        public function getWeatherMaskMC():MovieClip
        {
            return (_api.getWeatherMaskMC());
        }

        public function getShadowMC():MovieClip
        {
            return (_api.getShadowMC());
        }

        public function getShadowMaskMC():MovieClip
        {
            return (_api.getShadowMaskMC());
        }

        public function getHUDBackgroundMC():MovieClip
        {
            return (_api.getHUDBackgroundMC());
        }

        public function getHUDForegroundMC():MovieClip
        {
            return (_api.getHUDForegroundMC());
        }

        public function enableCeilingDeath(_arg_1:Boolean=true):void
        {
            _api.enableCeilingDeath(_arg_1);
        }

        public function enableFallDeath(_arg_1:Boolean=true):void
        {
            _api.enableFallDeath(_arg_1);
        }

        public function isCeilingDeathEnabled():Boolean
        {
            return (_api.isCeilingDeathEnabled());
        }

        public function isFallDeathEnabled():Boolean
        {
            return (_api.isFallDeathEnabled());
        }

        public function createTimer(_arg_1:int, _arg_2:int, _arg_3:Function, _arg_4:Object=null):void
        {
            _api.createTimer(_arg_1, _arg_2, _arg_3, _arg_4);
        }

        public function destroyTimer(_arg_1:Function):void
        {
            _api.destroyTimer(_arg_1);
        }

        public function toLocalPoint(_arg_1:DisplayObject):Point
        {
            return (_api.toLocalPoint(_arg_1));
        }

        public function getStartingPositionMCs():Array
        {
            return (_api.getStartingPositionMCs());
        }

        public function getSpawnPositionMCs():Array
        {
            return (_api.getSpawnPositionMCs());
        }

        public function getLightSourceMC():MovieClip
        {
            return (_api.getLightSourceMC());
        }

        public function getLedges():Array
        {
            return (_api.getLedges());
        }

        public function getCameraBounds():MovieClip
        {
            return (_api.getCameraBounds());
        }

        public function getDeathBounds():MovieClip
        {
            return (_api.getDeathBounds());
        }

        public function getSmashBallBounds():MovieClip
        {
            return (_api.getSmashBallBounds());
        }

        public function getItemSpawnBoundsList():Array
        {
            return (_api.getItemSpawnBoundsList());
        }

        public function getStarKOEnabled():Boolean
        {
            return (_api.getStarKOEnabled());
        }

        public function setStarKOEnabled(_arg_1:Boolean):void
        {
            _api.setStarKOEnabled(_arg_1);
        }

        public function getScreenKOEnabled():Boolean
        {
            return (_api.getScreenKOEnabled);
        }

        public function setScreenKOEnabled(_arg_1:Boolean):void
        {
            _api.setScreenKOEnabled(_arg_1);
        }


    }
}//package 


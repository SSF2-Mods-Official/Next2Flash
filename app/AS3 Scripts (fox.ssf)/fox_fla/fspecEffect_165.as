// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//fox_fla.fspecEffect_165

package fox_fla
{
    import flash.display.MovieClip;
    import flash.display.*;
    import flash.geom.*;
    import flash.events.*;
    import flash.media.*;
    import flash.filters.*;
    import flash.utils.*;
    import adobe.utils.*;
    import flash.accessibility.*;
    import flash.desktop.*;
    import flash.errors.*;
    import flash.external.*;
    import flash.globalization.*;
    import flash.net.*;
    import flash.net.drm.*;
    import flash.printing.*;
    import flash.profiler.*;
    import flash.sampler.*;
    import flash.sensors.*;
    import flash.system.*;
    import flash.text.*;
    import flash.text.ime.*;
    import flash.text.engine.*;
    import flash.ui.*;
    import flash.xml.*;

    public dynamic class fspecEffect_165 extends MovieClip 
    {

        public var self:*;
        public var timer:*;
        public var character:*;

        public function fspecEffect_165()
        {
            addFrameScript(0, this.frame1, 5, this.frame6);
        }

        public function lock():void
        {
            this.self.setX(this.character.getGlobalVariable(("dashX" + this.timer)));
            this.self.setY((this.character.getGlobalVariable(("dashY" + this.timer)) + 5));
            this.timer++;
            if (this.timer == (this.character.getGlobalVariable("dashLim") - 1))
            {
                this.self.destroy();
            };
        }

        public function remove(_arg_1:*):void
        {
            this.character.removeEventListener(SSF2Event.CHAR_HURT, this.remove);
            this.self.destroy();
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            this.timer = 0;
            if (((SSF2API.isReady()) && (this.self)))
            {
                this.character = this.self.getOwner();
                this.character.addEventListener(SSF2Event.CHAR_HURT, this.remove);
                this.self.createTimer(1, -1, this.lock);
            };
        }

        internal function frame6():*
        {
            this.gotoAndStop("loop");
        }


    }
}//package fox_fla


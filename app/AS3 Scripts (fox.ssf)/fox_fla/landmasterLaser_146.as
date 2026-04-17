// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//fox_fla.landmasterLaser_146

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

    public dynamic class landmasterLaser_146 extends MovieClip 
    {

        public var attackBox:MovieClip;
        public var self:*;
        public var FoxExt:*;

        public function landmasterLaser_146()
        {
            addFrameScript(0, this.frame1, 9, this.frame10);
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            if (((SSF2API.isReady()) && (this.self)))
            {
                this.FoxExt = this.self.getOwner();
            };
            if (((SSF2API.isReady()) && (this.self)))
            {
            };
        }

        internal function frame10():*
        {
            this.self.stancePlayFrame("loop");
        }


    }
}//package fox_fla


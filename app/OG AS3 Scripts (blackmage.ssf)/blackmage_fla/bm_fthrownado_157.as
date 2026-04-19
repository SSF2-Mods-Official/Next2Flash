// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.bm_fthrownado_157

package blackmage_fla
{
    import flash.display.MovieClip;
    import flash.geom.*;
    import flash.display.*;
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

    public dynamic class bm_fthrownado_157 extends MovieClip 
    {

        public var self:*;
        public var character:*;

        public function bm_fthrownado_157()
        {
            addFrameScript(0, this.frame1, 22, this.frame23);
        }

        public function remove(_arg_1:*):void
        {
            this.self.destroy();
            this.character.removeEventListener(SSF2Event.CHAR_HURT, this.remove);
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            if (((SSF2API.isReady()) && (this.self)))
            {
                this.character = this.self.getOwner();
                this.character.addEventListener(SSF2Event.CHAR_HURT, this.remove);
            };
        }

        internal function frame23():*
        {
            this.self.destroy();
        }


    }
}//package blackmage_fla


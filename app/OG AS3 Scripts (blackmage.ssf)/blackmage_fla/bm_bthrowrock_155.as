// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.bm_bthrowrock_155

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

    public dynamic class bm_bthrowrock_155 extends MovieClip 
    {

        public var hitBox:MovieClip;
        public var self:*;
        public var character:*;
        public var isOnGround:*;

        public function bm_bthrowrock_155()
        {
            addFrameScript(0, this.frame1, 3, this.frame4, 23, this.frame24);
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            if (((SSF2API.isReady()) && (this.self)))
            {
                this.character = this.self.getOwner();
            };
            this.visible = false;
            this.isOnGround = false;
            if (((SSF2API.isReady()) && (this.self)))
            {
                this.character.setGlobalVariable("bthrowProjectileDied", false);
            };
        }

        internal function frame4():*
        {
            this.isOnGround = this.self.isOnGround();
            if (!this.isOnGround)
            {
                this.character.setGlobalVariable("bthrowProjectileDied", true);
                this.self.destroy();
            };
            this.visible = true;
        }

        internal function frame24():*
        {
            this.self.destroy();
        }


    }
}//package blackmage_fla


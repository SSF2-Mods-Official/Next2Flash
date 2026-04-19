// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.FlareProjectile_179

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

    public dynamic class FlareProjectile_179 extends MovieClip 
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var self:*;

        public function FlareProjectile_179()
        {
            addFrameScript(0, this.frame1, 30, this.frame31, 55, this.frame56, 97, this.frame98);
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            if (((SSF2API.isReady()) && (this.self)))
            {
                this.self.updateAttackStats({"refreshRate":1});
                this.self.addToCamera();
            };
        }

        internal function frame31():*
        {
            this.self.updateAttackStats({"refreshRate":999});
            this.self.updateAttackBoxStats(1, {
                "hasEffect":true,
                "damage":26,
                "hitStun":6,
                "selfHitStun":6,
                "direction":30,
                "power":90,
                "kbConstant":100,
                "effectSound":"brawl_bomb_l",
                "effect_id":"effect_explosion"
            });
            this.self.updateAttackBoxStats(2, {
                "hasEffect":true,
                "damage":26,
                "hitStun":6,
                "selfHitStun":6,
                "direction":30,
                "power":90,
                "kbConstant":100,
                "effectSound":"brawl_bomb_l",
                "effect_id":"effect_explosion"
            });
            this.self.refreshAttackID();
        }

        internal function frame56():*
        {
            this.self.removeFromCamera();
        }

        internal function frame98():*
        {
            this.self.destroy();
        }


    }
}//package blackmage_fla


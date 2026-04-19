// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.NAir_69

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

    public dynamic class NAir_69 extends MovieClip 
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var attackBox3:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;

        public function NAir_69()
        {
            addFrameScript(0, this.frame1, 2, this.frame3, 3, this.frame4, 4, this.frame5, 6, this.frame7, 8, this.frame9, 10, this.frame11, 12, this.frame13, 14, this.frame15, 16, this.frame17, 22, this.frame23, 23, this.frame24, 24, this.frame25, 31, this.frame32);
        }

        public function setAngle(_arg_1:*=null):*
        {
            var _local_2:* = this.self.getYSpeed();
            var _local_3:* = this.self.getXSpeed();
            var _local_4:* = (Math.atan2(_local_2, _local_3) * (-180 / Math.PI));
            var _local_5:* = (Math.sqrt(((_local_2 * _local_2) + (_local_3 * _local_3))) * 4);
            if (!this.self.isFacingRight())
            {
                _local_4 = (180 - _local_4);
            };
            if (_local_4 < 0)
            {
                _local_4 = (_local_4 + 360);
            };
            this.self.updateAttackBoxStats(1, {
                "direction":_local_4,
                "power":_local_5
            });
            this.self.updateAttackBoxStats(2, {
                "direction":_local_4,
                "power":_local_5
            });
            this.self.updateAttackBoxStats(3, {
                "direction":_local_4,
                "power":_local_5
            });
            SSF2API.print(((_local_3.toString() + " | ") + _local_2.toString()));
            SSF2API.print(((_local_4.toString() + " | ") + _local_5.toString()));
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            if (((parent) && (SSF2API.isReady())))
            {
                this.self.setLandingLag(false);
            };
        }

        internal function frame3():*
        {
            this.self.attachEffect("global_spark", {
                "x":this.self.flipX(20),
                "y":-25
            });
            this.self.attachEffect("global_spark", {
                "x":this.self.flipX(-20),
                "y":-35
            });
            this.self.createTimer(1, -1, this.setAngle);
        }

        internal function frame4():*
        {
            this.self.playAttackSound(1);
            this.self.setLandingLag(true);
        }

        internal function frame5():*
        {
            this.self.refreshAttackID();
        }

        internal function frame7():*
        {
            this.self.refreshAttackID();
        }

        internal function frame9():*
        {
            this.self.refreshAttackID();
        }

        internal function frame11():*
        {
            this.self.refreshAttackID();
        }

        internal function frame13():*
        {
            this.self.refreshAttackID();
        }

        internal function frame15():*
        {
            this.self.refreshAttackID();
        }

        internal function frame17():*
        {
            this.self.destroyTimer(this.setAngle);
            this.self.updateAttackBoxStats(1, {
                "power":63,
                "weightKB":0,
                "kbConstant":80,
                "direction":45,
                "reversableAngle":true,
                "hitLag":-1,
                "hitStun":-1,
                "selfHitStun":-1
            });
            this.self.updateAttackBoxStats(2, {
                "power":63,
                "weightKB":0,
                "kbConstant":80,
                "direction":45,
                "reversableAngle":true,
                "hitLag":-1,
                "hitStun":-1,
                "selfHitStun":-1
            });
            this.self.updateAttackBoxStats(3, {
                "power":63,
                "weightKB":0,
                "kbConstant":80,
                "direction":45,
                "reversableAngle":true,
                "hitLag":-1,
                "hitStun":-1,
                "selfHitStun":-1
            });
            this.self.refreshAttackID();
            this.self.setLandingLag(false);
        }

        internal function frame23():*
        {
            this.self.endAttack();
        }

        internal function frame24():*
        {
            this.self.destroyTimer(this.setAngle);
            this.self.updateAttackBoxStats(1, {
                "damage":2,
                "power":63,
                "weightKB":0,
                "kbConstant":80,
                "direction":45,
                "reversableAngle":true,
                "hitLag":-1,
                "hitStun":-1,
                "selfHitStun":-1
            });
            this.self.updateAttackBoxStats(2, {
                "damage":2,
                "power":63,
                "weightKB":0,
                "kbConstant":80,
                "direction":45,
                "reversableAngle":true,
                "hitLag":-1,
                "hitStun":-1,
                "selfHitStun":-1
            });
            this.self.updateAttackBoxStats(3, {
                "damage":2,
                "power":63,
                "weightKB":0,
                "kbConstant":80,
                "direction":45,
                "reversableAngle":true,
                "hitLag":-1,
                "hitStun":-1,
                "selfHitStun":-1
            });
            this.self.refreshAttackID();
        }

        internal function frame25():*
        {
            SSF2API.getCamera().shake(3);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("blackmage_landHeavy");
            };
        }

        internal function frame32():*
        {
            this.self.endAttack();
        }


    }
}//package blackmage_fla


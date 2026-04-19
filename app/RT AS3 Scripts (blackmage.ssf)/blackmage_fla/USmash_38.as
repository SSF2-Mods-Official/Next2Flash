// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.USmash_38

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class USmash_38 extends MovieClip 
    {

        internal var attackBox:MovieClip;
        internal var attackBox2:MovieClip;
        internal var hitBox:MovieClip;
        internal var hitBox2:MovieClip;
        internal var hitBox3:MovieClip;
        internal var itemBox:MovieClip;
        internal var self:BlackMageExt;
        internal var xframe:String;

        public function USmash_38()
        {
            addFrameScript(0, this.frame1, 4, this.frame5, 44, this.frame45, 45, this.frame46, 46, this.frame47, 47, this.frame48, 61, this.frame62, 62, this.frame63, 63, this.frame64, 81, this.frame82, 86, this.frame87, 88, this.frame89, 90, this.frame91, 94, this.frame95, 128, this.frame129);
        }

        public function effects():void
        {
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(5),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame1():*
        {
            var _local_1:MovieClip;
            var _local_2:MovieClip;
            var _local_3:MovieClip;
            var _local_4:MovieClip;
            var _local_5:MovieClip;
            var _local_6:MovieClip;
            var _local_7:BlackMageExt;
            var _local_8:String;
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            };
            this.xframe = null;
        }

        internal function frame5():*
        {
            this.xframe = "charging";
            this.self.createTimer(4, -1, this.effects);
        }

        internal function frame45():*
        {
            this.self.stancePlayFrame("charging");
        }

        internal function frame46():*
        {
            this.xframe = "attack";
            this.self.destroyTimer(this.effects);
        }

        internal function frame47():*
        {
            this.self.playAttackSound(2);
            this.self.attachEffect("global_dust_cloud");
            this.self.attachEffect("global_dust_swirl");
            this.self.addEffectToList(this.self.attachEffect("blackmage_usmash_uncharged", {
                "scaleX":1.4,
                "scaleY":1.4,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame48():*
        {
            this.self.playAttackSound(3);
        }

        internal function frame62():*
        {
            this.self.attachEffect("effect_land");
            SSF2API.getCamera().shake(2);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("blackmage_landHeavy");
            };
        }

        internal function frame63():*
        {
            this.self.endAttack();
        }

        internal function frame64():*
        {
            this.xframe = "attack2";
            this.self.destroyTimer(this.effects);
            this.self.updateAttackStats({"refreshRate":1});
            this.self.updateAttackBoxStats(2, {
                "direction":20,
                "power":45,
                "damage":1,
                "hitStun":1,
                "selfHitStun":0,
                "priority":-1,
                "reversableAngle":false,
                "effectSound":"brawl_fire_m"
            });
            this.self.updateAttackBoxStats(1, {
                "direction":160,
                "power":45,
                "damage":1,
                "hitStun":1,
                "selfHitStun":0,
                "priority":-1,
                "reversableAngle":false,
                "effectSound":"brawl_fire_m"
            });
            this.self.playAttackSound(1);
        }

        internal function frame82():*
        {
            this.self.playAttackSound(2);
            this.self.updateAttackStats({"refreshRate":200});
            this.self.updateAttackBoxStats(1, {
                "direction":90,
                "power":10,
                "hitStun":17,
                "sdiDistance":0
            });
            this.self.refreshAttackID();
        }

        internal function frame87():*
        {
            this.self.attachEffect("global_sparkle", {"y":-20});
        }

        internal function frame89():*
        {
            this.self.updateAttackBoxStats(1, {
                "power":105,
                "kbConstant":50,
                "hitStun":1,
                "damage":15,
                "sdiDistance":1
            });
            this.self.refreshAttackID();
            SSF2API.getCamera().shake(7);
        }

        internal function frame91():*
        {
            this.self.updateAttackBoxStats(1, {"power":100});
        }

        internal function frame95():*
        {
            this.self.updateAttackBoxStats(1, {"damage":10});
        }

        internal function frame129():*
        {
            this.self.endAttack();
        }


    }
}//package blackmage_fla


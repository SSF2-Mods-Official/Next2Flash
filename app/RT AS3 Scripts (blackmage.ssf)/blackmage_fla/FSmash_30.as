// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.FSmash_30

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class FSmash_30 extends MovieClip 
    {

        internal var attackBox:MovieClip;
        internal var attackBox2:MovieClip;
        internal var attackBox3:MovieClip;
        internal var hitBox:MovieClip;
        internal var hitBox2:MovieClip;
        internal var itemBox:MovieClip;
        internal var self:BlackMageExt;
        internal var xframe:String;
        internal var projectile:*;

        public function FSmash_30()
        {
            addFrameScript(0, this.frame1, 3, this.frame4, 43, this.frame44, 44, this.frame45, 48, this.frame49, 51, this.frame52, 58, this.frame59, 74, this.frame75, 75, this.frame76, 86, this.frame87, 88, this.frame89, 99, this.frame100);
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
            var _local_9:*;
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            };
            this.xframe = null;
        }

        internal function frame4():*
        {
            this.xframe = "charging";
            this.self.createTimer(4, -1, this.effects);
        }

        internal function frame44():*
        {
            this.self.stancePlayFrame("charging");
        }

        internal function frame45():*
        {
            this.xframe = "attack";
            this.self.destroyTimer(this.effects);
        }

        internal function frame49():*
        {
            this.self.playSound("bmbolt");
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame52():*
        {
            this.self.attachEffect("global_dust_heavy");
            SSF2API.getCamera().shake(6);
        }

        internal function frame59():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":10,
                "kbConstant":75,
                "effect_id":"effect_elechit_light",
                "effectSound":"brawl_zap_m"
            });
            this.self.updateAttackBoxStats(2, {
                "damage":10,
                "kbConstant":75,
                "effect_id":"effect_elechit_light",
                "effectSound":"brawl_zap_m"
            });
            this.self.updateAttackBoxStats(3, {
                "damage":10,
                "kbConstant":75,
                "effect_id":"effect_elechit_light",
                "effectSound":"brawl_zap_m"
            });
        }

        internal function frame75():*
        {
            this.self.endAttack();
        }

        internal function frame76():*
        {
            this.xframe = "attack2";
            this.self.playSound("bm_whoosh");
            this.self.destroyTimer(this.effects);
        }

        internal function frame87():*
        {
            this.self.attachEffect("global_dust_swirl");
            this.self.attachEffect("global_sparkle", {
                "x":this.self.flipX(15),
                "y":-30
            });
        }

        internal function frame89():*
        {
            this.projectile = this.self.fireProjectile("fsmashfull");
        }

        internal function frame100():*
        {
            this.self.endAttack();
        }


    }
}//package blackmage_fla


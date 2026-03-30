package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_usmash_33 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;
        public var xframe:String;

        public function bomberman_usmash_33()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 43, this.frame44, 44, this.frame45, 51, this.frame52, 52, this.frame53, 61, this.frame62, 70, this.frame71);
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
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
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

        internal function frame52():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":13,
                "power":70,
                "direction":88,
                "kbConstant":75,
                "hitLag":-1,
                "burn":true,
                "effect_id":"effect_firehit_heavy"
            });
            this.self.updateAttackBoxStats(2, {
                "damage":13,
                "power":70,
                "direction":88,
                "kbConstant":75,
                "hitLag":-1,
                "burn":true,
                "effect_id":"effect_firehit_heavy"
            });
            this.self.refreshAttackID();
            this.self.attachEffectOverlay("effect_explosion", {
                "scaleX":1.37,
                "scaleY":1.37,
                "y":-73
            });
            this.self.attachEffect("global_dust_cloud", {
                "scaleX":0.8,
                "scaleY":0.8
            });
            this.self.attachEffect("global_dust_swirl", {"scaleX":1.5});
            SSF2API.getCamera().shake(8);
        }

        internal function frame53():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame62():*
        {
            SSF2API.getCamera().shake(2);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("bomberman_landHeavy");
            };
        }

        internal function frame71():*
        {
            this.self.endAttack();
        }


    }
}


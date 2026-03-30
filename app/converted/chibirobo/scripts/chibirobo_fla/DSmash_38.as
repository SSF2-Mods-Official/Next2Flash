package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class DSmash_38 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;
        public var xframe:*;

        public function DSmash_38()
        {
            super();
            addFrameScript(0, this.frame1, 7, this.frame8, 47, this.frame48, 48, this.frame49, 50, this.frame51, 51, this.frame52, 52, this.frame53, 54, this.frame55, 72, this.frame73);
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
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
            this.xframe = null;
        }

        internal function frame8():*
        {
            this.xframe = "charging";
            this.self.createTimer(4, -1, this.effects);
        }

        internal function frame48():*
        {
            this.self.stancePlayFrame("charging");
        }

        internal function frame49():*
        {
            this.xframe = "attack";
            this.self.destroyTimer(this.effects);
            this.self.fireProjectile("chibi_dsmashProj");
        }

        internal function frame51():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s1");
            };
        }

        internal function frame52():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame53():*
        {
            this.self.attachEffect("global_dust_swirl");
            SSF2API.getCamera().shake(5);
            if (SSF2API.isReady())
            {
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_land_s");
                }
                else
                {
                    this.self.playAttackSound(2);
                };
            };
        }

        internal function frame55():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":13,
                "effect_id":"effect_elechit_light",
                "direction":60,
                "power":25,
                "effectSound":"brawl_zap_m"
            });
        }

        internal function frame73():*
        {
            this.self.endAttack();
        }


    }
}


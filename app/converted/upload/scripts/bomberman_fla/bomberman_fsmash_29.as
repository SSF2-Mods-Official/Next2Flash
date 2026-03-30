package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_fsmash_29 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;
        public var xframe:String;

        public function bomberman_fsmash_29()
        {
            super();
            addFrameScript(0, this.frame1, 5, this.frame6, 45, this.frame46, 46, this.frame47, 49, this.frame50, 50, this.frame51, 67, this.frame68);
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

        internal function frame6():*
        {
            this.xframe = "charging";
            this.self.createTimer(4, -1, this.effects);
        }

        internal function frame46():*
        {
            this.self.stancePlayFrame("charging");
        }

        internal function frame47():*
        {
            this.xframe = "attack";
            this.self.destroyTimer(this.effects);
        }

        internal function frame50():*
        {
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(7),
                "scaleX":0.75,
                "scaleY":0.75
            });
            this.self.playAttackSound(1);
            this.self.addEffectToList(this.self.attachEffect("trail_bbm_fsmash", {
                "scaleX":1.35,
                "scaleY":1.35,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame51():*
        {
            this.self.attachEffect("effect_explosion", {
                "x":this.self.flipX(50),
                "scaleX":1.2,
                "scaleY":1.2,
                "x":50,
                "y":-15
            });
            this.self.updateAttackBoxStats(1, {
                "burn":true,
                "effect_id":"effect_firehit_heavy"
            });
            SSF2API.getCamera().shake(8);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m1");
            };
        }

        internal function frame68():*
        {
            this.self.endAttack();
        }


    }
}


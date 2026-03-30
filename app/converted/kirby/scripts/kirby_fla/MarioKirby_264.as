package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class MarioKirby_264 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var self:KirbyExt;
        public var mario_ground:Boolean;

        public function MarioKirby_264()
        {
            super();
            addFrameScript(0, this.frame1, 8, this.frame9, 17, this.frame18);
        }

        public function disableNeutralB():void
        {
            this.self.setAttackEnabled(false, "kirby_mario");
            this.self.createTimer(10, 1, this.enableNeutralB, {"persistent":true});
        }

        public function enableNeutralB():void
        {
            this.self.setAttackEnabled(true, "kirby_mario");
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.mario_ground = this.self.isOnGround();
                if (!this.mario_ground)
                {
                    this.self.updateAttackStats({
                        "allowControl":true,
                        "allowControlGround":false,
                        "cancelWhenAirborne":false
                    });
                };
            };
        }

        internal function frame9():*
        {
            this.self.fireProjectile("mario_fireball", 24, -18);
            if (this.self.isOnGround())
            {
                this.self.attachEffect("nSpecWave", {
                    "x":this.self.flipX(27),
                    "y":-14
                });
                this.self.attachEffect("global_dust_heavy", {
                    "x":this.self.flipX(5),
                    "y":1,
                    "scaleX":-0.5,
                    "scaleY":-0.5
                });
            }
            else
            {
                this.self.attachEffect("nSpecWave", {
                    "x":this.self.flipX(27),
                    "y":-14,
                    "rotation":this.self.flipX(20)
                });
            };
            this.self.playSound("mario_fireballspawn");
            this.self.playSound("mario_fireballsfx");
        }

        internal function frame18():*
        {
            this.disableNeutralB();
            this.self.endAttack();
        }


    }
}


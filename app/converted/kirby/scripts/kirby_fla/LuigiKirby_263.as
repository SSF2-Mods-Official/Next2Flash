package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class LuigiKirby_263 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var self:KirbyExt;
        public var luigi_ground:Boolean;

        public function LuigiKirby_263()
        {
            super();
            addFrameScript(0, this.frame1, 8, this.frame9, 17, this.frame18);
        }

        public function disableNeutralB():void
        {
            this.self.setAttackEnabled(false, "kirby_luigi");
            this.self.createTimer(12, 1, this.enableNeutralB, {"persistent":true});
        }

        public function enableNeutralB():void
        {
            this.self.setAttackEnabled(true, "kirby_luigi");
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.luigi_ground = this.self.isOnGround();
                if (!this.luigi_ground)
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
            this.self.fireProjectile("luigi_fireball", 20, -18);
            this.self.attachEffect("nSpecWaveG", {
                "x":this.self.flipX(20),
                "y":-15
            });
            if (this.self.isOnGround())
            {
                this.self.attachEffect("global_dust_light");
            };
            this.self.playSound("luigi_fireball_sfx");
        }

        internal function frame18():*
        {
            this.disableNeutralB();
            this.self.endAttack();
        }


    }
}


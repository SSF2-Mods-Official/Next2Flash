package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class SoraKirby_301 extends MovieClip
    {

        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var self:KirbyExt;

        public function SoraKirby_301()
        {
            super();
            addFrameScript(0, this.frame1, 8, this.frame9, 40, this.frame41, 49, this.frame50, 58, this.frame59);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            if (SSF2API.isReady() && this.self && !this.self.isOnGround())
            {
                this.self.updateAttackStats({
                    "xSpeedDecayAir":-1,
                    "air_ease":2
                });
            };
        }

        internal function frame9():*
        {
            this.self.fireProjectile("sora_strikeraid");
            this.self.playVoiceSound(1);
            this.self.playAttackSound(1);
            this.self.attachEffect("global_dust_light");
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m2");
            };
        }

        internal function frame41():*
        {
            this.self.endAttack();
        }

        internal function frame50():*
        {
            this.self.endAttack();
        }

        internal function frame59():*
        {
            this.self.endAttack();
        }


    }
}


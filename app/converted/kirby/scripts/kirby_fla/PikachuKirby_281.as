package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class PikachuKirby_281 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;

        public function PikachuKirby_281()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 6, this.frame7, 7, this.frame8, 8, this.frame9, 27, this.frame28);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
        }

        internal function frame2():*
        {
            this.self.playVoiceSound(1);
        }

        internal function frame7():*
        {
            this.self.attachEffect("pika_elec_nspec", {
                "scaleX":1.4,
                "scaleY":1.4,
                "x":this.self.flipX(-10),
                "parentLock":true
            });
        }

        internal function frame8():*
        {
            this.self.fireProjectile("thunderJolt");
            this.self.attachEffect("global_dust_light");
        }

        internal function frame9():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame28():*
        {
            this.self.endAttack();
        }


    }
}


package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class BombermanKirby_194 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;

        public function BombermanKirby_194()
        {
            super();
            addFrameScript(0, this.frame1, 10, this.frame11, 13, this.frame14, 16, this.frame17, 27, this.frame28);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setupHatEffect(1, -30, -44);
            };
        }

        internal function frame11():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame14():*
        {
            this.self.playVoiceSound(1);
        }

        internal function frame17():*
        {
            this.self.fireProjectile("kirbyBManBomb");
        }

        internal function frame28():*
        {
            this.self.endAttack();
        }


    }
}


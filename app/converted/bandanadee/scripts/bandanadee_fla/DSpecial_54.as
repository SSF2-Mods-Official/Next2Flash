package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class DSpecial_54 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;

        public function DSpecial_54()
        {
            super();
            addFrameScript(0, this.frame1, 9, this.frame10, 11, this.frame12, 13, this.frame14, 15, this.frame16, 17, this.frame18, 19, this.frame20, 21, this.frame22, 23, this.frame24, 25, this.frame26, 38, this.frame39);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
        }

        internal function frame10():*
        {
            this.self.setXSpeed(18, false);
            this.self.playAttackSound(1);
            this.self.playAttackSound(2);
            this.self.playAttackSound(3);
            this.self.playVoiceSound(1);
        }

        internal function frame12():*
        {
            this.self.playAttackSound(2);
        }

        internal function frame14():*
        {
            this.self.playAttackSound(2);
        }

        internal function frame16():*
        {
            this.self.playAttackSound(2);
        }

        internal function frame18():*
        {
            this.self.playAttackSound(2);
            this.self.updateAttackBoxStats(1, {"damage":12});
        }

        internal function frame20():*
        {
            this.self.playAttackSound(2);
        }

        internal function frame22():*
        {
            this.self.playAttackSound(2);
        }

        internal function frame24():*
        {
            this.self.playAttackSound(2);
        }

        internal function frame26():*
        {
            this.self.setXSpeed(0);
        }

        internal function frame39():*
        {
            this.self.endAttack();
        }


    }
}


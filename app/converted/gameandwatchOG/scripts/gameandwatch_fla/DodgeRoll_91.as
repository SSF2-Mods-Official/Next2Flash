package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class DodgeRoll_91 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;
        public var effect:*;

        public function DodgeRoll_91()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 5, this.frame6, 8, this.frame9, 13, this.frame14, 15, this.frame16);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
        }

        internal function frame2():*
        {
            this.effect = this.self.attachEffect("global_dust_heavy", {
                "scaleX":0.8,
                "scaleY":0.8
            });
            this.effect.scaleX = -(this.effect.scaleX);
        }

        internal function frame3():*
        {
            this.self.setIntangibility(true);
        }

        internal function frame6():*
        {
            this.self.playSound("beep_step_1");
        }

        internal function frame9():*
        {
            this.self.playSound("beep_step_2");
            this.self.setIntangibility(false);
        }

        internal function frame14():*
        {
            this.self.playSound("beep_step_1");
        }

        internal function frame16():*
        {
            this.self.endAttack();
        }


    }
}


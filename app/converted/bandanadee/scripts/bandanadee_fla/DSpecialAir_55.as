package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class DSpecialAir_55 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;

        public function DSpecialAir_55()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 5, this.frame6, 11, this.frame12, 13, this.frame14, 15, this.frame16, 17, this.frame18, 19, this.frame20, 21, this.frame22, 23, this.frame24, 25, this.frame26, 31, this.frame32, 33, this.frame34, 38, this.frame39, 39, this.frame40, 48, this.frame49);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            if (this.self && SSF2API.isReady())
            {
                this.self.setLandingLag(true);
            };
        }

        internal function frame2():*
        {
            this.self.setXSpeed((this.self.getXSpeed() * 0.3));
        }

        internal function frame6():*
        {
            this.self.playSound("throw_woosh");
        }

        internal function frame12():*
        {
            this.self.setXSpeed(7, false);
            this.self.setYSpeed(9);
            this.self.updateAttackStats({"air_ease":-1});
            this.self.playAttackSound(1);
            this.self.playAttackSound(2);
            this.self.playAttackSound(3);
            this.self.playVoiceSound(1);
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
            this.self.playAttackSound(2);
        }

        internal function frame32():*
        {
            this.self.updateAttackStats({
                "allowDoubleJump":false,
                "doubleJumpCancelAttack":false
            });
        }

        internal function frame34():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame39():*
        {
            this.self.endAttack();
        }

        internal function frame40():*
        {
            this.self.updateAttackStats({
                "allowDoubleJump":false,
                "refreshRate":9999
            });
            this.self.refreshAttackID();
            this.self.attachEffect("effect_bdee_land", {"y":-18});
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            };
        }

        internal function frame49():*
        {
            this.self.endAttack();
        }


    }
}


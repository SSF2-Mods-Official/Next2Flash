package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class FSmash_100 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var self:KirbyExt;
        public var xframe:String;

        public function FSmash_100()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 41, this.frame42, 42, this.frame43, 46, this.frame47, 48, this.frame49, 65, this.frame66);
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
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            this.xframe = null;
        }

        internal function frame2():*
        {
            this.xframe = "charging";
            this.self.createTimer(4, -1, this.effects);
        }

        internal function frame42():*
        {
            this.gotoAndStop("charging");
        }

        internal function frame43():*
        {
            this.xframe = "attack";
            this.self.destroyTimer(this.effects);
            this.self.playVoiceSound(1);
            this.self.playAttackSound(1);
            this.self.setXSpeed(12, false);
        }

        internal function frame47():*
        {
            this.self.attachEffect("global_dust_heavy");
            this.self.attachEffect("global_dust_blast", {
                "x":this.self.flipX(37),
                "y":-25,
                "parentLock":true
            });
        }

        internal function frame49():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":13,
                "power":50,
                "kbConstant":96
            });
        }

        internal function frame66():*
        {
            this.self.endAttack();
        }


    }
}


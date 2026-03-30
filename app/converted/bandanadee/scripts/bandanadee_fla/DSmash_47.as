package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class DSmash_47 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;
        public var xframe:String;

        public function DSmash_47()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 43, this.frame44, 44, this.frame45, 46, this.frame47, 50, this.frame51, 65, this.frame66);
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
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            this.xframe = null;
        }

        internal function frame4():*
        {
            this.xframe = "charging";
            this.self.createTimer(4, -1, this.effects);
        }

        internal function frame44():*
        {
            this.self.stancePlayFrame("charging");
        }

        internal function frame45():*
        {
            this.xframe = "attack";
            this.self.destroyTimer(this.effects);
        }

        internal function frame47():*
        {
            this.self.playAttackSound(1);
            this.self.playVoiceSound(1);
        }

        internal function frame51():*
        {
            this.self.updateAttackBoxStats(1, {
                "direction":70,
                "damage":8
            });
        }

        internal function frame66():*
        {
            this.self.endAttack();
        }


    }
}


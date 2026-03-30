package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class LuffyKirby_262 extends MovieClip
    {

        public var grabBox:MovieClip;
        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var touchBox:MovieClip;
        public var self:KirbyExt;
        public var opponent:*;
        public var count:*;

        public function LuffyKirby_262()
        {
            super();
            addFrameScript(0, this.frame1, 6, this.frame7, 10, this.frame11, 35, this.frame36, 36, this.frame37, 45, this.frame46, 46, this.frame47, 47, this.frame48, 49, this.frame50, 51, this.frame52, 53, this.frame54, 77, this.frame78);
        }

        public function frameCount(_arg_1:*=null):*
        {
            this.count++;
        }

        public function toDecide(_arg_1:*=null):*
        {
            this.opponent = this.self.getGrabbedOpponent();
            this.self.stancePlayFrame("decide");
        }

        public function decide(_arg_1:*=null):*
        {
            this.self.setXSpeed(0);
            this.self.setYSpeed(0);
            this.opponent.setXSpeed(0);
            this.opponent.setYSpeed(0);
        }

        public function toDragging():void
        {
            this.self.destroyTimer(this.decide);
            this.self.playSound("grab");
            this.self.stancePlayFrame(("dragging" + this.count.toString()));
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            this.opponent = null;
            this.count = 0;
            if (this.self && SSF2API.isReady())
            {
                this.self.addEventListener(SSF2Event.CHAR_GRAB, this.toDecide);
            };
        }

        internal function frame7():*
        {
            this.self.createTimer(1, 0, this.frameCount);
            this.self.playAttackSound(1);
            this.self.playVoiceSound(1);
        }

        internal function frame11():*
        {
            this.self.destroyTimer(this.frameCount);
        }

        internal function frame36():*
        {
            this.self.endAttack();
        }

        internal function frame37():*
        {
            this.self.destroyTimer(this.frameCount);
            this.self.createTimer(1, 0, this.decide);
            this.self.stancePlayFrame(("decide" + this.count.toString()));
        }

        internal function frame46():*
        {
            this.toDragging();
        }

        internal function frame47():*
        {
            this.toDragging();
        }

        internal function frame48():*
        {
            this.toDragging();
        }

        internal function frame50():*
        {
            this.toDragging();
        }

        internal function frame52():*
        {
            this.toDragging();
        }

        internal function frame54():*
        {
            this.toDragging();
        }

        internal function frame78():*
        {
            if (this.self.isOnGround())
            {
                this.self.toGrabbing();
            }
            else
            {
                this.opponent.setXSpeed(8, false);
            };
            this.self.toGrabbing();
        }


    }
}

